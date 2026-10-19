"""The workbench: an agent chat beside the generated UI and the code behind it."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Collection, Coroutine, Mapping
from pathlib import Path
from typing import Any

from ipywidgets import Widget

import anylumino as al
from anylumino import astryx as ax

from . import codegen, openui
from . import session as store
from .agents import AgentError, AgentRunner, Failed, Text, ToolFinished, ToolStarted
from .app import App
from .export import CallbacksError, app_class, handler_names, ui_class, write_module
from .export_dialog import ExportDialog
from .prompt import system_prompt
from .reply import ReplyError, split_reply


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
    agent : str | None, default None
        The CLI to run each turn with: ``"claude"`` or ``"codex"``. Defaults
        to the agent of a restored session, or ``"claude"``.
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
    height : int | float | str | None, default 640
        CSS height of the workbench.

    Raises
    ------
    ValueError
        If ``agent`` differs from the agent of the restored session, since a
        session resumes the agent's own conversation.

    Notes
    -----
    The workbench runs agent-written Python in this kernel: the callbacks and
    the generated UI code. Both are shown in the code tabs.
    """

    def __init__(
        self,
        agent: str | None = None,
        session: str | None = None,
        namespace: Mapping[str, Any] | None = None,
        cwd: str | Path | None = None,
        *,
        height: int | float | str | None = 640,
    ) -> None:
        saved = store.load(session) if session else None
        if saved is not None and agent is not None and agent != saved.agent:
            raise ValueError(f"Session {session!r} runs {saved.agent}; pass agent={saved.agent!r} or another session name.")

        self.state = saved or store.SessionState(
            name=session or "", agent=agent or "claude", cwd=str(Path(cwd or os.getcwd()).resolve())
        )
        self.namespace = dict(namespace or {})
        self.runner = AgentRunner(
            self.state.agent, Path(self.state.cwd), self.state.name or "anylumino", self.state.agent_session_id
        )
        self.ui_code = ""
        self.last_error = ""
        self.running = False
        self.tasks: set[asyncio.Task[Any]] = set()

        self.chat = ax.Chat(self.state.messages, placeholder="Describe the UI to build", height="100%")
        self.status = ax.StatusDot("Ready", variant="neutral")
        # Astryx shows a status dot's label only to screen readers, so a caption repeats it
        self.status_text = ax.Text("Ready", text_type="supporting")
        self.export_dialog = ExportDialog(self.export)
        self.export_button = ax.Button(
            "Export",
            size="sm",
            disabled=True,
            # Session names may hold `-`, which an importable module name cannot
            callbacks=[lambda _button: self.export_dialog.open_with((self.state.name or "ui").replace("-", "_"))],
        )
        header = ax.Stack(
            [
                ax.Badge(self.state.agent, variant="info"),
                ax.Badge(self.state.name or "unsaved"),
                self.status,
                self.status_text,
                self.export_button,
                self.export_dialog,
            ],
            direction="horizontal",
            gap=2,
            align="center",
            height=HEADER_HEIGHT,
            padding=2,
        )
        self.ui_host = al.ScrollBox([self.empty_ui()], height="100%")
        self.code_views = {
            "openui": ax.CodeBlock("", language="text", width="100%"),
            "ui_code": ax.CodeBlock("", language="python", width="100%"),
            "callbacks": ax.CodeBlock("", language="python", width="100%"),
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

    @staticmethod
    def empty_ui() -> ax.EmptyState:
        return ax.EmptyState("No UI yet", description="Ask the agent for one in the chat.")

    def submit(self, text: str, context: Any = None) -> None:
        """Start a turn with ``text``; refused with a system message while a turn runs."""
        if self.running:
            self.add_message("system", "A turn is already running; wait for it or stop it.")

            return

        # Set before the turn starts, so that a second submit in the meantime is refused
        self.set_running(True)
        self.runner.stopped = False
        self.schedule(self.run_turn(text, context))

    def ask_agent(self, message: str, context: Any = None) -> None:
        """Send ``message`` to the agent as if the user had typed it."""
        self.submit(message, context)

    def schedule(self, coroutine: Coroutine[Any, Any, Any]) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(coroutine)

            return

        task = loop.create_task(coroutine)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

    async def run_turn(self, text: str, context: Any = None) -> None:
        try:
            self.add_message("user", text, "sent")
            index = self.add_message("assistant", "", "sending")
            await self.stream_reply(index, text, context)
        finally:
            self.state.agent_session_id = self.runner.session_id
            self.set_running(False)
            self.save()

    async def stream_reply(self, index: int, text: str, context: Any) -> None:
        reply = ""
        tools: list[dict[str, Any]] = []
        failure = ""
        # At most one chat update per interval, and the last one always lands.
        loop = asyncio.get_running_loop()
        flush: asyncio.TimerHandle | None = None

        def flush_reply() -> None:
            nonlocal flush
            flush = None
            self.update_reply(index, reply, tools, "sending")

        try:
            async for event in self.runner.turn(self.turn_prompt(text, context), await system_prompt(self.namespace)):
                if isinstance(event, Text):
                    reply += event.text
                elif isinstance(event, ToolStarted):
                    tools.append({"id": event.id, "name": event.name, "target": event.target, "status": "running"})
                elif isinstance(event, ToolFinished):
                    for tool in tools:
                        if tool["id"] == event.id:
                            tool["status"] = "error" if event.error else "complete"
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
            self.update_reply(index, reply, tools, "stopped")
        elif failure:
            self.update_reply(index, reply, tools, "error")
            self.add_message("system", f"The agent failed: {failure}")
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
        self.add_message("system", f"The reply was not applied; the UI is unchanged. {message}")

    async def apply(self, program: str, callbacks: str) -> None:
        """Build the UI from ``program`` and ``callbacks``, then update all tabs at once."""
        result = await openui.parse(program)
        if result["errors"] or result["incomplete"]:
            details = "; ".join(f"{error.get('statementId', '?')}: {error['message']}" for error in result["errors"])
            raise ApplyError(f"OpenUI errors: {details or 'the program is incomplete'}")

        cls = self.compile_callbacks(callbacks)
        try:
            source = codegen.generate(result, handler_names(cls), self.namespace)
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
        self.add_message("system", f"Callback `{name}` raised {type(error).__name__}: {error}")

    async def restore(self) -> None:
        if not self.state.program:
            return

        try:
            await self.apply(self.state.program, self.state.callbacks)
        except Exception as error:
            message = str(error) if isinstance(error, (ApplyError, openui.OpenUIError)) else f"{type(error).__name__}: {error}"
            self.ui_host.widgets = [ax.EmptyState("The saved UI could not be built", description=message)]
            self.show_code(openui=self.state.program, callbacks=self.state.callbacks)

    def export(self, folder: Path, name: str) -> None:
        """Write the UI code and callbacks into one file in ``folder`` and post the ``load`` call for it."""
        try:
            path = shown_path(write_module(folder, name, self.ui_code, self.state.callbacks))
        except OSError as error:
            self.add_message("system", f"Export failed: {error}")

            return

        arguments = [json.dumps(path), *(f"{key}={key}" for key in self.namespace)]
        # As an assistant message, since the chat shows system messages on one line without markdown
        self.add_message(
            "assistant",
            f"Exported `{path}`. Show the same UI in a notebook cell with:\n\n"
            f"```python\nfrom anylumino.workbench import load\n\nload({', '.join(arguments)})\n```",
        )

    def turn_prompt(self, text: str, context: Any) -> str:
        parts = [text]
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

    def add_message(self, role: str, content: str, status: str | None = None) -> int:
        """Append a chat message and return its index."""
        self.set_messages([*self.chat.messages, chat_message(role, content, status)])

        return len(self.chat.messages) - 1

    # Updates the turn's reply by index, since other messages can arrive while it streams
    def update_reply(self, index: int, content: str, tools: list[dict[str, Any]], status: str | None = None) -> None:
        messages = list(self.chat.messages)
        messages[index] = chat_message("assistant", content, status, tools)
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
    role: str, content: str, status: str | None = None, tools: list[dict[str, Any]] | None = None
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

    for child in getattr(widget, "widgets", None) or []:
        if isinstance(child, Widget):
            close_tree(child, keep)

    widget.close()


def shown_path(path: Path) -> str:
    """Return ``path`` relative to the current directory when it is inside it."""
    try:
        return str(path.resolve().relative_to(Path.cwd()))
    except ValueError:
        return str(path.resolve())
