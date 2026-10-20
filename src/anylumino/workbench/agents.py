"""Run one chat turn with the local `claude` or `codex` CLI and stream what it does."""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import re
import shutil
import signal
import tempfile
import uuid
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import skill
from .skill import Skill


AGENTS = ("claude", "codex")
CLAUDE_TOOLS = "Read,Grep,Glob,Skill"
STOP_GRACE = 3.0
_PLACEHOLDER_TRANSPORTS = {"stdio": 'command="true"', "streamable_http": 'url="http://127.0.0.1:9"'}


class AgentError(RuntimeError):
    """The turn could not start or the CLI reported a failure."""


@dataclass(frozen=True)
class Session:
    id: str


@dataclass(frozen=True)
class Text:
    text: str


@dataclass(frozen=True)
class ToolStarted:
    id: str
    name: str
    target: str


@dataclass(frozen=True)
class ToolFinished:
    id: str
    error: bool


@dataclass(frozen=True)
class Failed:
    message: str


Event = Session | Text | ToolStarted | ToolFinished | Failed


class ClaudeStream:
    """Turn `claude -p --output-format stream-json` lines into events."""

    def __init__(self) -> None:
        self.wrote = False

    def feed(self, line: str) -> list[Event]:
        data = json.loads(line)
        kind = data.get("type")
        if kind == "system" and data.get("subtype") == "init":
            return [Session(data["session_id"])]

        if kind == "stream_event":
            return self.stream_event(data["event"])

        if kind == "assistant":
            return [
                ToolStarted(block["id"], block["name"], _target(block.get("input", {})))
                for block in data["message"]["content"]
                if block.get("type") == "tool_use"
            ]

        if kind == "user":
            content = data["message"].get("content")
            if not isinstance(content, list):
                return []

            return [
                ToolFinished(block["tool_use_id"], bool(block.get("is_error")))
                for block in content
                if block.get("type") == "tool_result"
            ]

        if kind == "result" and data.get("is_error"):
            return [Failed(str(data.get("result") or data.get("subtype")))]

        return []

    def stream_event(self, event: dict[str, Any]) -> list[Event]:
        if event.get("type") == "content_block_start" and event["content_block"].get("type") == "text":
            return [Text("\n\n")] if self.wrote else []

        delta = event.get("delta", {}) if event.get("type") == "content_block_delta" else {}
        if delta.get("type") == "text_delta" and delta["text"]:
            self.wrote = True

            return [Text(delta["text"])]

        return []


class CodexStream:
    """Turn `codex exec --json` lines into events."""

    def __init__(self) -> None:
        self.wrote = False

    def feed(self, line: str) -> list[Event]:
        data = json.loads(line)
        kind = data.get("type")
        if kind == "thread.started":
            return [Session(data["thread_id"])]

        if kind in ("turn.failed", "error"):
            error = data.get("error") or {}

            return [Failed(str(error.get("message") or data.get("message") or kind))]

        item = data.get("item") or {}
        item_type = item.get("type")
        if item_type == "agent_message" and kind == "item.completed":
            text = item["text"]
            events: list[Event] = [Text("\n\n")] if self.wrote else []
            self.wrote = True

            return [*events, Text(text)]

        if item_type in (None, "agent_message", "reasoning"):
            return []

        if kind == "item.started":
            return [ToolStarted(item["id"], item_type, _target(item))]

        if kind == "item.completed":
            failed = item.get("status") == "failed" or item.get("exit_code") not in (None, 0)

            return [ToolFinished(item["id"], failed)]

        return []


def _target(fields: dict[str, Any]) -> str:
    for key in ("file_path", "path", "pattern", "command", "query"):
        if isinstance(fields.get(key), str):
            return fields[key]

    return ""


def claude_argv(
    session_id: str,
    resume: bool,
    name: str,
    system_prompt: str,
    model: str | None = None,
    effort: str | None = None,
    skills: Sequence[Skill] = (),
    plugin: Path | None = None,
) -> list[str]:
    session = ["--resume", session_id] if resume else ["--session-id", session_id, "-n", name]
    settings = [*(["--model", model] if model else []), *(["--effort", effort] if effort else [])]
    # The plugin loads the notebook skills, and --add-dir lets Read open the files they point to
    notebook = ["--plugin-dir", str(plugin)] if plugin else []
    notebook += [part for notebook_skill in skills for part in ("--add-dir", str(notebook_skill.path))]

    return [
        "claude",
        "-p",
        "--output-format",
        "stream-json",
        "--verbose",
        "--include-partial-messages",
        *session,
        "--append-system-prompt",
        system_prompt,
        "--strict-mcp-config",
        "--plugin-dir",
        str(skill.PLUGIN),
        *notebook,
        "--tools",
        CLAUDE_TOOLS,
        "--allowedTools",
        CLAUDE_TOOLS,
        "--permission-mode",
        "dontAsk",
        *settings,
    ]


def codex_argv(
    session_id: str | None,
    cwd: Path,
    system_prompt: str,
    mcp_overrides: list[str],
    model: str | None = None,
    effort: str | None = None,
) -> list[str]:
    # Config overrides rather than `-m`, since they apply the same way to a resumed thread
    settings = {"model": model, "model_reasoning_effort": effort}
    overrides = [*mcp_overrides, *(f"{key}={json.dumps(value)}" for key, value in settings.items() if value)]
    disabled = [part for override in overrides for part in ("-c", override)]
    if session_id:
        return [
            "codex",
            "exec",
            "resume",
            session_id,
            "--json",
            "--skip-git-repo-check",
            "-c",
            'sandbox_mode="read-only"',
            *disabled,
            "-",
        ]

    return [
        "codex",
        "exec",
        "--json",
        "-s",
        "read-only",
        "--skip-git-repo-check",
        "-C",
        str(cwd),
        "-c",
        f"developer_instructions={json.dumps(system_prompt)}",
        *disabled,
        "-",
    ]


async def codex_mcp_overrides(cwd: Path) -> list[str]:
    """Return config overrides that turn off every MCP server `codex` would start.

    The read-only sandbox does not cover MCP tools. Plugin servers have no entry in
    ``config.toml``, so ``enabled=false`` alone leaves them without a transport;
    each override replaces the transport with a placeholder that never starts.
    """
    process = await asyncio.create_subprocess_exec(
        shutil.which("codex") or "codex",
        "mcp",
        "list",
        "--json",
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    output, errors = await process.communicate()
    try:
        servers = json.loads(output)
    except json.JSONDecodeError:
        message = errors.decode().strip()[-2000:]
        raise AgentError(f"`codex mcp list --json` failed, so its MCP servers cannot be turned off: {message}") from None

    overrides = []
    for server in servers:
        name = server["name"]
        if not server.get("enabled"):
            continue

        transport = _PLACEHOLDER_TRANSPORTS.get(server.get("transport", {}).get("type"))
        if transport is None or not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            raise AgentError(f"The codex MCP server {name!r} cannot be turned off.")

        overrides.append(f"mcp_servers.{name}={{{transport},enabled=false}}")

    return overrides


class AgentRunner:
    """Run turns of one agent session, one at a time.

    ``session_id`` is the agent's own session ID once a turn has recorded it;
    later turns resume it. ``model`` and ``effort`` go to the CLI's model and
    reasoning effort settings for each turn; `None` keeps the CLI's default. ``stopped`` is set by `stop` and stays set until the
    caller clears it for the next turn, so a stop that comes before the
    process starts still cancels the turn.
    """

    def __init__(
        self,
        agent: str,
        cwd: Path,
        name: str,
        session_id: str | None = None,
        model: str | None = None,
        effort: str | None = None,
        skills: Sequence[Skill] = (),
    ) -> None:
        if agent not in AGENTS:
            raise AgentError(f"Unknown agent {agent!r}; expected one of {', '.join(AGENTS)}.")

        self.agent = agent
        self.cwd = cwd
        self.name = name
        self.session_id = session_id
        self.model = model
        self.effort = effort
        self.skills = list(skills)
        self.process: asyncio.subprocess.Process | None = None
        self.stopped = False

    @property
    def running(self) -> bool:
        return self.process is not None

    async def turn(self, prompt: str, system_prompt: str) -> AsyncIterator[Event]:
        """Run one turn and yield its events; raise `AgentError` when it cannot run."""
        if self.running:
            raise AgentError("A turn is already running.")

        if shutil.which(self.agent) is None:
            raise AgentError(f"`{self.agent}` was not found on PATH.")

        # Holds the plugin that links the notebook skills for `claude`, for this turn only
        plugins = tempfile.TemporaryDirectory(prefix="anylumino-skills-")
        if self.agent == "claude":
            resume = self.session_id is not None
            session_id = self.session_id or str(uuid.uuid4())
            plugin = skill.write_plugin(self.skills, Path(plugins.name)) if self.skills else None
            argv = claude_argv(
                session_id, resume, self.name, system_prompt, self.model, self.effort, self.skills, plugin
            )
            stream: ClaudeStream | CodexStream = ClaudeStream()
        else:
            overrides = await codex_mcp_overrides(self.cwd)
            argv = codex_argv(self.session_id, self.cwd, system_prompt, overrides, self.model, self.effort)
            stream = CodexStream()

        if self.stopped:
            plugins.cleanup()

            return

        self.process = await asyncio.create_subprocess_exec(
            shutil.which(argv[0]) or argv[0],
            *argv[1:],
            cwd=self.cwd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
            limit=16 * 1024 * 1024,
        )
        process = self.process
        try:
            assert process.stdin is not None and process.stdout is not None and process.stderr is not None
            process.stdin.write(prompt.encode())
            await process.stdin.drain()
            process.stdin.close()
            stderr = asyncio.ensure_future(process.stderr.read())
            async for line in process.stdout:
                if not line.strip():
                    continue

                for event in stream.feed(line.decode()):
                    if isinstance(event, Session):
                        self.session_id = event.id

                    yield event

            code = await process.wait()
            errors = (await stderr).decode().strip()
            if code != 0 and not self.stopped:
                yield Failed(f"`{self.agent}` exited with {code}: {errors[-2000:]}")
        finally:
            if process.returncode is None:
                await self.terminate(process)

            self.process = None
            plugins.cleanup()

    async def stop(self) -> None:
        """Stop the current turn, including one whose process has not started yet."""
        self.stopped = True
        if self.process is not None:
            await self.terminate(self.process)

    @staticmethod
    async def terminate(process: asyncio.subprocess.Process) -> None:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGTERM)

        try:
            await asyncio.wait_for(process.wait(), STOP_GRACE)
        except TimeoutError:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)

            await process.wait()
