"""The workbench: an agent chat beside the generated UI and the code behind it."""

from __future__ import annotations

import asyncio
import contextvars
import json
import os
import sys
import threading
from collections.abc import Callable, Collection, Coroutine, Mapping, Sequence
from pathlib import Path
from typing import Any

from ipywidgets import Widget

import anylumino as al
from anylumino import astryx as ax
from anylumino.astryx import ChatRole, MessageStatus, ToolCallStatus

from . import catalog, codegen, openui
from . import session as store
from .agents import Agent, AgentError, AgentRunner, Failed, Text, ToolFinished, ToolStarted
from .app import App, View
from .export import (
    CallbacksError,
    ExportedFileError,
    app_class,
    class_source,
    handler_names,
    read_module,
    ui_class,
    ui_fingerprint,
    write_module,
)
from .file_dialogs import ExportDialog, ImportDialog
from .prompt import system_prompt
from .reply import ReplyError, split_reply
from .skill import read_skill


TABS = {"ui": "UI", "openui": "OpenUI", "ui_code": "UI code", "callbacks": "Callbacks"}
STREAM_INTERVAL = 0.05
HEADER_HEIGHT = 40
# The callbacks of a UI without handlers, so that it still has an App to export
EMPTY_CALLBACKS = """from anylumino.workbench import App


class UIApp(App):
    pass
"""


class ApplyError(RuntimeError):
    """A turn's program or callbacks could not be applied; nothing changed."""


class Workbench(al.SplitPanel):
    """Build notebook UIs by chatting with a local coding agent.

    Parameters
    ----------
    agent : Agent | str | None, default None
        The CLI to run each turn with, `Agent.CLAUDE` or `Agent.CODEX`, or
        their values ``"claude"`` and ``"codex"``. Defaults to the agent of a
        restored session, or `Agent.CLAUDE`.
    session : str | None, default None
        Session name. A named session is saved after every turn under
        ``~/.anylumino/sessions/<session>.json`` and restored when a workbench
        is created with the same name, including the agent's own session.
    namespace : Mapping[str, Any] | None, default None
        Names the callbacks can read, such as data frames. Widgets in it can be
        mounted with ``Widget(name)``. The agent sees each name and type.
    cwd : str | Path | None, default None
        Directory the agent runs in. Defaults to the current directory, or the
        directory stored with a restored session.
    model : str | None, default None
        The model the agent CLI runs, such as ``"sonnet"`` for Claude Code.
        Defaults to the restored session's model, or the CLI's own default.
    effort : str | None, default None
        The reasoning effort: ``low``, ``medium``, ``high``, ``xhigh``, or
        ``max`` for Claude Code, and ``minimal``, ``low``, ``medium``,
        ``high``, or ``xhigh`` for Codex. Defaults to the restored session's
        effort, or the CLI's own default.
    skills : Sequence[str | Path] | None, default None
        Skill folders that document the notebook's own libraries, such as a
        charting library the callbacks import. Each holds a ``SKILL.md`` with
        ``name`` and ``description`` front matter, in the Claude Code skill
        format. The agent sees each name and description and loads a skill when
        it needs it. A ``components.py`` in the folder adds OpenUI components
        for the library's widgets. Defaults to the restored session's skills.
    prompt : str | None, default None
        A first message to send as soon as the workbench is created, as if typed
        in the chat. In a notebook the turn runs in the background while the
        workbench shows; it runs again each time the cell runs. A restored
        session continues its conversation with it.
    height : int | float | str | None, default 640
        CSS height of the workbench.

    Raises
    ------
    ValueError
        If ``agent`` differs from the agent of the restored session, since a
        session resumes the agent's own conversation, or a skill folder has no
        valid ``SKILL.md``.

    Notes
    -----
    The workbench runs agent-written Python in this kernel: the callbacks and
    the generated UI code. Both are shown in the code tabs.
    """

    def __init__(
        self,
        agent: Agent | str | None = None,
        session: str | None = None,
        namespace: Mapping[str, Any] | None = None,
        cwd: str | Path | None = None,
        *,
        model: str | None = None,
        effort: str | None = None,
        skills: Sequence[str | Path] | None = None,
        prompt: str | None = None,
        height: int | float | str | None = 640,
    ) -> None:
        saved = store.load(session) if session else None
        if saved is not None and agent is not None and agent != saved.agent:
            raise ValueError(f"Session {session!r} runs {saved.agent}; pass agent={saved.agent!r} or another session name.")

        self.state = saved or store.SessionState(
            name=session or "", agent=Agent(agent or Agent.CLAUDE), cwd=str(Path(cwd or os.getcwd()).resolve())
        )
        # A restored session resumes the agent's conversation with new settings when they are given
        self.state.model = model or self.state.model
        self.state.effort = effort or self.state.effort
        if skills is not None:
            self.state.skills = [str(Path(folder).expanduser().resolve()) for folder in skills]

        self.skills = [read_skill(folder) for folder in self.state.skills]
        # The built-in catalog plus the components the skills add
        self.components = catalog.extend(component for entry in self.skills for component in entry.components)
        self.namespace = dict(namespace or {})
        self.runner = AgentRunner(
            self.state.agent,
            Path(self.state.cwd),
            self.state.name or "anylumino",
            self.state.agent_session_id,
            self.state.model,
            self.state.effort,
            self.skills,
        )
        self.ui_code = ""
        # The current generated UI, a View whose widget the UI tab shows
        self.ui: View | None = None
        self.last_error = ""
        self.running = False
        self.tasks: set[asyncio.Task[Any]] = set()
        self.marimo_loop = marimo_turn_loop()

        self.chat = ax.Chat(self.state.messages, placeholder="Describe the UI to build", height="100%")
        self.status = ax.StatusDot("Ready", variant="neutral")
        # Astryx shows a status dot's label only to screen readers, so a caption repeats it
        self.status_text = ax.Text("Ready", text_type="supporting")
        self.export_dialog = ExportDialog(self.export, self.run_on_turn_loop)
        self.export_button = ax.Button(
            "Export",
            size="sm",
            disabled=True,
            # Session names may hold `-`, which an importable module name cannot
            callbacks=[lambda _button: self.export_dialog.open_with((self.state.name or "ui").replace("-", "_"))],
        )
        self.import_dialog = ImportDialog(self.import_file, self.run_on_turn_loop)
        self.import_button = ax.Button(
            "Import", size="sm", callbacks=[lambda _button: self.import_dialog.open_in_last_folder()]
        )
        header = ax.Stack(
            [
                ax.Badge(" ".join(filter(None, [self.state.agent, self.state.model, self.state.effort])), variant="info"),
                ax.Badge(self.state.name or "unsaved"),
                self.status,
                self.status_text,
                self.export_button,
                self.import_button,
                self.export_dialog,
                self.import_dialog,
            ],
            direction="horizontal",
            gap=2,
            align="center",
            height=HEADER_HEIGHT,
            padding=2,
        )
        self.ui_host = al.ScrollBox([self.empty_ui()], height="100%")
        self.code_views = {
            "openui": ax.CodeBlock("", language="text", line_numbers=True, width="100%"),
            "ui_code": ax.CodeBlock("", language="python", line_numbers=True, width="100%"),
            "callbacks": ax.CodeBlock("", language="python", line_numbers=True, width="100%"),
        }
        self.tabs = al.TabPanel(
            {"ui": self.ui_host, **{key: al.ScrollBox([view], height="100%") for key, view in self.code_views.items()}},
            titles=TABS,
            height="100%",
        )
        super().__init__(
            [al.VBox([header, self.chat], stretches=[0, 1], child_min_height=HEADER_HEIGHT, height="100%"), self.tabs],
            sizes=[0.35, 0.65],
            height=height,
        )
        # Without this, keys pressed in a read-only code tab act as notebook command-mode shortcuts
        self.suppress_shortcuts = True
        self.chat.on_submit(lambda _chat, text: self.submit(text))
        self.chat.on_stop(lambda _chat: self.schedule(self.runner.stop()))
        if saved is not None:
            self.schedule(self.restore())

        if prompt:
            self.submit(prompt)

    @staticmethod
    def empty_ui() -> ax.EmptyState:
        return ax.EmptyState("No UI yet", description="Ask the agent for one in the chat.")

    def submit(self, text: str, context: Any = None) -> None:
        """Start a turn with ``text``; refused with a system message while a turn runs."""
        if self.running:
            self.add_message(ChatRole.SYSTEM, "A turn is already running; wait for it or stop it.")

            return

        # Set before the turn starts, so that a second submit in the meantime is refused
        self.set_running(True)
        self.runner.stopped = False
        self.schedule(self.run_turn(text, context))

    def import_file(self, path: str | Path) -> None:
        """Fill the tabs from an exported file, and ask the agent to reconcile it when it was edited.

        The program and callbacks of the file apply as a turn's would. When they
        do not apply, or the file's ``UI`` class differs from the code the
        program generates, a turn sends the file to the agent to update the
        program and callbacks.
        """
        if self.running:
            self.add_message(ChatRole.SYSTEM, "A turn is already running; wait for it or stop it.")

            return

        self.set_running(True)
        self.runner.stopped = False
        self.schedule(self.run_import(Path(path)))

    def ask_agent(self, message: str, context: Any = None) -> None:
        """Send ``message`` to the agent as if the user had typed it."""
        self.submit(message, context)

    def schedule(self, coroutine: Coroutine[Any, Any, Any]) -> None:
        if self.marimo_loop is not None:
            loop, context = self.marimo_loop
            loop.call_soon_threadsafe(self.start_task, loop, coroutine, context)

            return

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(coroutine)

            return

        self.start_task(loop, coroutine)

    def start_task(
        self,
        loop: asyncio.AbstractEventLoop,
        coroutine: Coroutine[Any, Any, Any],
        context: contextvars.Context | None = None,
    ) -> None:
        task = loop.create_task(coroutine, context=context)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

    def run_on_turn_loop(self, call: Callable[[], None]) -> None:
        """Run ``call`` on the marimo turn loop, so that it can create widgets, or at once outside marimo."""
        if self.marimo_loop is None:
            call()

            return

        loop, context = self.marimo_loop
        loop.call_soon_threadsafe(call, context=context)

    async def run_import(self, path: Path) -> None:
        shown = shown_path(path)
        try:
            source = path.read_text()
            reason = await self.apply_import(source)
        except (OSError, ExportedFileError) as error:
            self.add_message(ChatRole.SYSTEM, f"Import of `{shown}` failed: {error}")
            self.set_running(False)

            return

        if not reason:
            self.last_error = ""
            self.add_message(ChatRole.SYSTEM, f"Imported `{shown}`.")
            self.set_running(False)
            self.save()

            return

        details = (
            f"The file `{shown}` was exported from this workbench and changed outside it, and {reason}. "
            "Reply with the openui-lang program and the python callbacks that reproduce this file: "
            "the program must generate its UI class, and the callbacks must keep its App class.\n\n"
            f"```text\n{source}\n```"
        )
        await self.run_turn(f"Reconcile the imported file `{shown}`: {reason}.", details=details)
        self.report_reconcile(shown, source)

    # Reports whether the agent's reply reproduces the file's UI class, since a valid reply can
    # still miss a hand edit; a file that is not valid Python has no class to compare
    def report_reconcile(self, shown: str, source: str) -> None:
        if self.last_error or self.runner.stopped:
            return

        try:
            target = class_source(source, "UI")
        except SyntaxError:
            return

        if ui_fingerprint(class_source(self.ui_code, "UI")) == ui_fingerprint(target):
            self.add_message(ChatRole.SYSTEM, f"Reconciled `{shown}`: the generated UI class matches the file.")
        else:
            self.add_message(
                ChatRole.SYSTEM,
                f"The generated UI class still differs from `{shown}`. The UI code tab shows what applied; "
                "ask the agent in the chat to close the gap.",
            )

        self.save()

    async def apply_import(self, source: str) -> str:
        """Apply an exported file's program and callbacks; return why the agent must reconcile it, or ``""``."""
        try:
            exported = read_module(source)
        except SyntaxError as error:
            return f"it is not valid Python: {error.msg} (line {error.lineno})"

        try:
            await self.apply(exported.program, exported.callbacks)
        except Exception as error:
            return f"it does not apply: {error}"

        if exported.ui_edited and ui_fingerprint(class_source(self.ui_code, "UI")) != ui_fingerprint(exported.ui_class):
            return "its UI class was edited, so it differs from the code its program generates"

        return ""

    async def run_turn(self, text: str, context: Any = None, details: str = "") -> None:
        try:
            self.add_message(ChatRole.USER, text, MessageStatus.SENT)
            index = self.add_message(ChatRole.ASSISTANT, "", MessageStatus.SENDING)
            await self.stream_reply(index, text, context, details)
        finally:
            self.state.agent_session_id = self.runner.session_id
            self.set_running(False)
            self.save()

    async def stream_reply(self, index: int, text: str, context: Any, details: str = "") -> None:
        reply = ""
        tools: list[dict[str, Any]] = []
        failure = ""
        # At most one chat update per interval, and the last one always lands.
        loop = asyncio.get_running_loop()
        flush: asyncio.TimerHandle | None = None

        def flush_reply() -> None:
            nonlocal flush
            flush = None
            self.update_reply(index, reply, tools, MessageStatus.SENDING)

        try:
            async for event in self.runner.turn(self.turn_prompt(text, context, details), await system_prompt(self.namespace, self.skills, self.components)):
                if isinstance(event, Text):
                    reply += event.text
                elif isinstance(event, ToolStarted):
                    tools.append({"id": event.id, "name": event.name, "target": event.target, "status": ToolCallStatus.RUNNING})
                elif isinstance(event, ToolFinished):
                    for tool in tools:
                        if tool["id"] == event.id:
                            tool["status"] = ToolCallStatus.ERROR if event.error else ToolCallStatus.COMPLETE
                elif isinstance(event, Failed):
                    failure = event.message

                if flush is None:
                    flush = loop.call_later(STREAM_INTERVAL, flush_reply)
        except (AgentError, openui.OpenUIError) as error:
            failure = str(error)
        except Exception as error:
            failure = f"{type(error).__name__}: {error}"

        if flush is not None:
            flush.cancel()

        if self.runner.stopped:
            self.update_reply(index, reply, tools, MessageStatus.STOPPED)
        elif failure:
            self.update_reply(index, reply, tools, MessageStatus.ERROR)
            self.add_message(ChatRole.SYSTEM, f"The agent failed: {failure}")
        else:
            await self.finish_reply(index, reply, tools)

    async def finish_reply(self, index: int, reply: str, tools: list[dict[str, Any]]) -> None:
        self.last_error = ""
        try:
            parts = split_reply(reply)
        except ReplyError as error:
            self.update_reply(index, reply, tools)
            self.report_apply_error(str(error))

            return

        self.update_reply(index, parts.prose, tools)
        if parts.program is None and parts.callbacks is None:
            return

        callbacks = (self.state.callbacks or EMPTY_CALLBACKS) if parts.callbacks is None else parts.callbacks
        try:
            program = await openui.merge(self.state.program, parts.program) if parts.program else self.state.program
            await self.apply(program, callbacks)
        except (ApplyError, openui.OpenUIError) as error:
            self.report_apply_error(str(error))
        except Exception as error:
            self.report_apply_error(f"{type(error).__name__}: {error}")

    def report_apply_error(self, message: str) -> None:
        self.last_error = message
        self.add_message(ChatRole.SYSTEM, f"The reply was not applied; the UI is unchanged. {message}")

    async def apply(self, program: str, callbacks: str) -> None:
        """Build the UI from ``program`` and ``callbacks``, then update all tabs at once."""
        result = await openui.parse(program, self.components)
        if result["errors"] or result["incomplete"]:
            details = "; ".join(f"{error.get('statementId', '?')}: {error['message']}" for error in result["errors"])
            raise ApplyError(f"OpenUI errors: {details or 'the program is incomplete'}")

        cls = self.compile_callbacks(callbacks)
        try:
            source = codegen.generate(result, handler_names(cls), self.namespace, self.components)
        except codegen.GenerationError as error:
            raise ApplyError(f"UI code: {error}") from error

        try:
            app = cls(**self.namespace)
        except ValueError as error:
            raise ApplyError(f"Namespace: {error}") from error

        app.agent = self.ask_agent
        app.on_error = self.report_callback_error
        try:
            ui = ui_class(source)(app)
        except Exception as error:
            raise ApplyError(f"Building the UI raised {type(error).__name__}: {error}") from error

        self.state.program = program
        self.state.callbacks = callbacks
        self.ui_code = source
        previous = self.ui_host.widgets
        self.ui = ui
        self.ui_host.widgets = [ui]
        keep = {id(value) for value in self.namespace.values() if isinstance(value, Widget)}
        for widget in previous:
            close_tree(widget, keep)

        self.export_button.disabled = False
        self.show_code(openui=program, ui_code=source, callbacks=callbacks)

    def compile_callbacks(self, callbacks: str) -> type[App]:
        try:
            return app_class(callbacks)
        except SyntaxError as error:
            raise ApplyError(f"Callbacks failed to compile: {error.msg} (line {error.lineno})") from error
        except CallbacksError as error:
            raise ApplyError(f"Callbacks: {error}") from error
        except Exception as error:
            raise ApplyError(f"Callbacks raised {type(error).__name__}: {error}") from error

    def report_callback_error(self, name: str, error: Exception) -> None:
        self.add_message(ChatRole.SYSTEM, f"Callback `{name}` raised {type(error).__name__}: {error}")

    async def restore(self) -> None:
        if not self.state.program:
            return

        try:
            await self.apply(self.state.program, self.state.callbacks)
        except Exception as error:
            message = str(error) if isinstance(error, (ApplyError, openui.OpenUIError)) else f"{type(error).__name__}: {error}"
            self.ui_host.widgets = [ax.EmptyState("The saved UI could not be built", description=message)]
            self.show_code(openui=self.state.program, callbacks=self.state.callbacks)

    def export(self, path: str | Path) -> None:
        """Write the UI code and callbacks into the file ``path``, such as ``"exports/sales.py"``.

        An existing file is replaced. The chat shows the ``load`` call for the
        file, or why nothing was written.
        """
        if not self.ui_code:
            self.add_message(ChatRole.SYSTEM, "Export failed: there is no UI yet.")

            return

        try:
            write_module(Path(path), self.ui_code, self.state.callbacks, self.state.program)
        except OSError as error:
            self.add_message(ChatRole.SYSTEM, f"Export failed: {error}")

            return

        shown = shown_path(Path(path))
        arguments = [json.dumps(shown), *(f"{key}={key}" for key in self.namespace)]
        # As an assistant message, since the chat shows system messages on one line without markdown
        self.add_message(
            ChatRole.ASSISTANT,
            f"Exported `{shown}`. Show the same UI in a notebook cell with:\n\n"
            f"```python\nfrom anylumino.workbench import load\n\nload({', '.join(arguments)})\n```",
        )

    # ``details`` reach the agent but not the chat, such as an imported file's source
    def turn_prompt(self, text: str, context: Any, details: str = "") -> str:
        parts = [text, *([details] if details else [])]
        if context is not None:
            parts.append(f"Context from the UI: {json.dumps(context, default=str)}")

        if self.last_error:
            parts.append(f"Your previous reply was not applied: {self.last_error}")

        if self.state.program:
            parts.append(f"Current program:\n```openui-lang\n{self.state.program}\n```")

        if self.state.callbacks:
            parts.append(f"Current callbacks:\n```python\n{self.state.callbacks}```")

        return "\n\n".join(parts)

    def show_code(self, **texts: str) -> None:
        for key, text in texts.items():
            view = self.code_views[key]
            view.props = {**view.props, "code": text}

    def add_message(self, role: ChatRole, content: str, status: MessageStatus | None = None) -> int:
        """Append a chat message and return its index."""
        self.set_messages([*self.chat.messages, chat_message(role, content, status)])

        return len(self.chat.messages) - 1

    # Updates the turn's reply by index, since other messages can arrive while it streams
    def update_reply(
        self, index: int, content: str, tools: list[dict[str, Any]], status: MessageStatus | None = None
    ) -> None:
        messages = list(self.chat.messages)
        messages[index] = chat_message(ChatRole.ASSISTANT, content, status, tools)
        self.set_messages(messages)

    def set_messages(self, messages: list[dict[str, Any]]) -> None:
        self.chat.messages = messages
        self.state.messages = messages

    def set_running(self, running: bool) -> None:
        self.running = running
        self.chat.is_streaming = running
        self.status.label = self.status_text.text = "Running" if running else "Ready"
        self.status.variant = "accent" if running else "neutral"
        self.status.props = {**self.status.props, "isPulsing": running}

    def save(self) -> None:
        if self.state.name:
            store.save(self.state)


# A finished reply has no status, so the chat shows no delivery label under it
def chat_message(
    role: ChatRole, content: str, status: MessageStatus | None = None, tools: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    message: dict[str, Any] = {"role": role, "content": content}
    if status:
        message["status"] = status

    if tools:
        message["tool_calls"] = [{key: tool[key] for key in ("name", "target", "status")} for tool in tools]

    return message


def close_tree(widget: Widget, keep: Collection[int]) -> None:
    """Close ``widget`` and the widgets it holds, except those whose ``id`` is in ``keep``."""
    if id(widget) in keep:
        return

    # Only a `widgets` trait holds children: ipywidgets' class-level `Widget.widgets` raises on instances
    for child in widget.widgets if widget.has_trait("widgets") else []:
        if isinstance(child, Widget):
            close_tree(child, keep)

    widget.close()


def shown_path(path: Path) -> str:
    """Return ``path`` relative to the current directory when it is inside it."""
    try:
        return str(path.resolve().relative_to(Path.cwd()))
    except ValueError:
        return str(path.resolve())


def marimo_turn_loop() -> tuple[asyncio.AbstractEventLoop, contextvars.Context] | None:
    """Start an event loop for workbench turns on a `mo.Thread` when this runs in a marimo cell.

    marimo closes the widgets a cell creates when the cell reruns, so it only
    lets work the cell started create widgets, and a turn builds the reply's
    widgets after the cell has run. A `mo.Thread` started here belongs to the
    cell, so turns run on its loop, in its context, can build them; the loop
    stops when marimo tells the thread to exit. Elsewhere, such as in
    JupyterLab, turns run on the kernel's own loop and this returns `None`.
    """
    if "marimo" not in sys.modules:
        return None

    import marimo as mo

    if not mo.running_in_notebook():
        return None

    ready = threading.Event()
    started: list[tuple[asyncio.AbstractEventLoop, contextvars.Context]] = []

    def run() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        started.append((loop, contextvars.copy_context()))
        ready.set()

        async def until_exit() -> None:
            thread = mo.current_thread()
            while not thread.should_exit:
                await asyncio.sleep(0.2)

        try:
            loop.run_until_complete(until_exit())
        finally:
            loop.close()

    mo.Thread(target=run, daemon=True).start()
    ready.wait()

    return started[0]
