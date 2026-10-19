"""The workbench: an agent chat beside the generated UI and the code behind it."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Callable, Coroutine, Mapping
from pathlib import Path
from typing import Any

import anylumino as al
from anylumino import astryx as ax

from . import codegen, openui
from . import session as store
from .agents import AgentError, AgentRunner, Failed, Text, ToolFinished, ToolStarted
from .prompt import SETUP, system_prompt
from .reply import ReplyError, split_reply


TABS = {"ui": "UI", "openui": "OpenUI", "ui_code": "UI code", "callbacks": "Callbacks"}
STREAM_INTERVAL = 0.05
HEADER_HEIGHT = 40


class ApplyError(RuntimeError):
    """A turn's program or callbacks could not be applied; nothing changed."""


class Workbench(al.SplitPanel):
    """Build notebook UIs by chatting with a local coding agent.

    Parameters
    ----------
    agent : str, default 'claude'
        The CLI to run each turn with: ``"claude"`` or ``"codex"``.
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

    Notes
    -----
    The workbench runs agent-written Python in this kernel: the callbacks and
    the generated UI code. Both are shown in the code tabs.
    """

    def __init__(
        self,
        agent: str = "claude",
        session: str | None = None,
        namespace: Mapping[str, Any] | None = None,
        cwd: str | Path | None = None,
        *,
        height: int | float | str | None = 640,
    ) -> None:
        saved = store.load(session) if session else None
        self.state = saved or store.SessionState(
            name=session or "", agent=agent, cwd=str(Path(cwd or os.getcwd()).resolve())
        )
        self.namespace = dict(namespace or {})
        self.runner = AgentRunner(
            self.state.agent, Path(self.state.cwd), self.state.name or "anylumino", self.state.agent_session_id
        )
        self.ui_code = ""
        self.last_error = ""
        self.tasks: set[asyncio.Task[Any]] = set()

        self.chat = ax.Chat(self.state.messages, placeholder="Describe the UI to build", height="100%")
        self.status = ax.StatusDot("Ready", variant="neutral")
        # Astryx shows a status dot's label only to screen readers, so a caption repeats it
        self.status_text = ax.Text("Ready", text_type="supporting")
        header = ax.Stack(
            [ax.Badge(self.state.agent, variant="info"), ax.Badge(self.state.name or "unsaved"), self.status, self.status_text],
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
        if self.runner.running:
            self.add_message("system", "A turn is already running; wait for it or stop it.")
            return
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
        self.add_message("user", text, "sent")
        self.add_message("assistant", "", status="sending")
        self.set_running(True)
        reply = ""
        tools: list[dict[str, Any]] = []
        failure = ""
        # At most one chat update per interval, and the last one always lands.
        loop = asyncio.get_running_loop()
        flush: asyncio.TimerHandle | None = None

        def flush_reply() -> None:
            nonlocal flush
            flush = None
            self.update_reply(reply, tools, "sending")

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
        if flush is not None:
            flush.cancel()
        try:
            if self.runner.stopped:
                self.update_reply(reply, tools, "stopped")
            elif failure:
                self.update_reply(reply, tools, "error")
                self.add_message("system", f"The agent failed: {failure}")
            else:
                await self.finish_reply(reply, tools)
        finally:
            self.state.agent_session_id = self.runner.session_id
            self.set_running(False)
            self.save()

    async def finish_reply(self, reply: str, tools: list[dict[str, Any]]) -> None:
        try:
            parts = split_reply(reply)
        except ReplyError as error:
            self.update_reply(reply, tools)
            self.report_apply_error(str(error))
            return
        self.update_reply(parts.prose, tools)
        if parts.program is None and parts.callbacks is None:
            return
        callbacks = self.state.callbacks if parts.callbacks is None else parts.callbacks
        try:
            program = await openui.merge(self.state.program, parts.program) if parts.program else self.state.program
            await self.apply(program, callbacks)
        except (ApplyError, openui.OpenUIError) as error:
            self.report_apply_error(str(error))
        else:
            self.last_error = ""

    def report_apply_error(self, message: str) -> None:
        self.last_error = message
        self.add_message("system", f"The reply was not applied; the UI is unchanged. {message}")

    async def apply(self, program: str, callbacks: str) -> None:
        """Build the UI from ``program`` and ``callbacks``, then update all tabs at once."""
        result = await openui.parse(program)
        if result["errors"] or result["incomplete"]:
            details = "; ".join(f"{error.get('statementId', '?')}: {error['message']}" for error in result["errors"])
            raise ApplyError(f"OpenUI errors: {details or 'the program is incomplete'}")
        handlers = self.compile_callbacks(callbacks)
        try:
            source = codegen.generate(result, handlers, self.namespace)
        except codegen.GenerationError as error:
            raise ApplyError(f"UI code: {error}") from error
        module: dict[str, Any] = {"__name__": "anylumino_workbench_ui"}
        try:
            exec(compile(source, "ui.py", "exec"), module)
            root, widgets = module["build"](handlers, self.namespace, self.ask_agent)
        except Exception as error:
            raise ApplyError(f"Building the UI raised {type(error).__name__}: {error}") from error
        if SETUP in handlers:
            handlers[SETUP](widgets)
        self.state.program = program
        self.state.callbacks = callbacks
        self.ui_code = source
        self.ui_host.widgets = [root]
        for key, text in (("openui", program), ("ui_code", source), ("callbacks", callbacks)):
            view = self.code_views[key]
            view.props = {**view.props, "code": text}

    def compile_callbacks(self, callbacks: str) -> dict[str, Callable[..., None]]:
        scope: dict[str, Any] = {**self.namespace, "ask_agent": self.ask_agent, "__name__": "anylumino_workbench_callbacks"}
        try:
            exec(compile(callbacks, "callbacks.py", "exec"), scope)
        except SyntaxError as error:
            raise ApplyError(f"Callbacks failed to compile: {error.msg} (line {error.lineno})") from error
        except Exception as error:
            raise ApplyError(f"Callbacks raised {type(error).__name__}: {error}") from error
        return {
            name: self.guarded(name, value)
            for name, value in scope.items()
            if callable(value) and getattr(value, "__module__", None) == "anylumino_workbench_callbacks"
        }

    def guarded(self, name: str, handler: Callable[..., None]) -> Callable[..., None]:
        def run(*args: Any) -> None:
            try:
                handler(*args)
            except Exception as error:
                self.add_message("system", f"Callback `{name}` raised {type(error).__name__}: {error}")

        return run

    async def restore(self) -> None:
        if not self.state.program:
            return
        try:
            await self.apply(self.state.program, self.state.callbacks)
        except (ApplyError, openui.OpenUIError) as error:
            self.ui_host.widgets = [ax.EmptyState("The saved UI could not be built", description=str(error))]
            for key, text in (("openui", self.state.program), ("callbacks", self.state.callbacks)):
                view = self.code_views[key]
                view.props = {**view.props, "code": text}

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

    def add_message(self, role: str, content: str, status: str | None = None) -> None:
        message: dict[str, Any] = {"role": role, "content": content}
        if status:
            message["status"] = status
        self.chat.messages = [*self.chat.messages, message]
        self.state.messages = self.chat.messages

    # A finished reply has no status, so the chat shows no delivery label under it
    def update_reply(self, content: str, tools: list[dict[str, Any]], status: str | None = None) -> None:
        message: dict[str, Any] = {"role": "assistant", "content": content}
        if status:
            message["status"] = status
        if tools:
            message["tool_calls"] = [{key: tool[key] for key in ("name", "target", "status")} for tool in tools]
        self.chat.messages = [*self.chat.messages[:-1], message]
        self.state.messages = self.chat.messages

    def set_running(self, running: bool) -> None:
        self.chat.is_streaming = running
        self.status.label = self.status_text.text = "Running" if running else "Ready"
        self.status.variant = "accent" if running else "neutral"
        self.status.props = {**self.status.props, "isPulsing": running}

    def save(self) -> None:
        if self.state.name:
            store.save(self.state)
