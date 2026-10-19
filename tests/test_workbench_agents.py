import asyncio
import json
import time
from pathlib import Path

import pytest

from anylumino.workbench.agents import (
    AgentError,
    AgentRunner,
    Failed,
    Session,
    Text,
    ToolFinished,
    ToolStarted,
)
from anylumino.workbench.reply import Reply, ReplyError, split_reply
from anylumino.workbench.skill import PLUGIN


FIXTURES = Path(__file__).parent / "fixtures" / "agents"
CLAUDE_SESSION = "d564292f-fdb7-41da-a88d-555ad70e93f5"
MCP_SERVERS = json.dumps(
    [
        {"name": "chrome-devtools", "enabled": True, "transport": {"type": "stdio"}},
        {"name": "old", "enabled": False, "transport": {"type": "stdio"}},
        {"name": "docs", "enabled": True, "transport": {"type": "streamable_http"}},
    ]
)
MCP_OFF = [
    "-c", 'mcp_servers.chrome-devtools={command="true",enabled=false}',
    "-c", 'mcp_servers.docs={url="http://127.0.0.1:9",enabled=false}',
]
CODEX_THREAD = "01a14ffe-6124-72d0-9368-530f48c6095d"

def run_turn(runner, prompt="Hi", system_prompt="SYSTEM"):
    async def collect():
        return [event async for event in runner.turn(prompt, system_prompt)]

    return asyncio.run(collect())


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Here it is.\n```openui-lang\nroot = VBox([])\n```\nAnd handlers:\n```python\ndef f(event, widgets):\n    pass\n```\nDone.",
            Reply("Here it is.\n\nAnd handlers:\n\nDone.", "root = VBox([])", "def f(event, widgets):\n    pass\n"),
        ),
        ("Layout only.\n```openui\nroot = VBox([])\n```", Reply("Layout only.", "root = VBox([])", None)),
        ("Handlers only.\n```python\nx = 1\n```", Reply("Handlers only.", None, "x = 1\n")),
        ("Just an answer.", Reply("Just an answer.", None, None)),
        ("Shell:\n```bash\nls\n```", Reply("Shell:\n```bash\nls\n```", None, None)),
    ],
    ids=["both", "program-only", "callbacks-only", "neither", "other-fence-kept"],
)
def test_split_reply(text, expected):
    assert split_reply(text) == expected


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("```openui\na = 1\n```\n```openui-lang\nb = 2\n```", "The reply has 2 `openui` blocks; send at most one."),
        ("```python\na = 1\n```\n```python\nb = 2\n```", "The reply has 2 `python` blocks; send at most one."),
    ],
    ids=["two-programs", "two-callbacks"],
)
def test_split_reply_rejects_duplicates(text, message):
    with pytest.raises(ReplyError, match=f"^{message}$"):
        split_reply(text)


def test_claude_first_turn_then_resume(fake_cli, monkeypatch, tmp_path):
    runner = AgentRunner("claude", tmp_path, "sales")
    monkeypatch.setenv("FAKE_STREAM", str(FIXTURES / "claude" / "first.jsonl"))
    first = run_turn(runner, "Read note.txt")
    monkeypatch.setenv("FAKE_STREAM", str(FIXTURES / "claude" / "resume.jsonl"))
    second = run_turn(runner, "What did it say?")

    first_call, second_call = fake_cli()
    generated = first_call["argv"][first_call["argv"].index("--session-id") + 1]
    assert first_call["argv"] == [
        "-p", "--output-format", "stream-json", "--verbose", "--include-partial-messages",
        "--session-id", generated, "-n", "sales", "--append-system-prompt", "SYSTEM",
        "--strict-mcp-config", "--plugin-dir", str(PLUGIN), "--tools", "Read,Grep,Glob,Skill",
        "--allowedTools", "Read,Grep,Glob,Skill", "--permission-mode", "dontAsk",
    ]
    assert second_call["argv"] == [
        "-p", "--output-format", "stream-json", "--verbose", "--include-partial-messages",
        "--resume", CLAUDE_SESSION, "--append-system-prompt", "SYSTEM",
        "--strict-mcp-config", "--plugin-dir", str(PLUGIN), "--tools", "Read,Grep,Glob,Skill",
        "--allowedTools", "Read,Grep,Glob,Skill", "--permission-mode", "dontAsk",
    ]
    assert (first_call["stdin"], second_call["stdin"]) == ("Read note.txt", "What did it say?")
    assert first_call["cwd"] == str(tmp_path.resolve())
    assert [event for event in first if not isinstance(event, Text)] == [
        Session(CLAUDE_SESSION),
        ToolStarted("toolu_01BFMJXAsKzpUKETZdz9YU64", "Read", "/work/note.txt"),
        ToolFinished("toolu_01BFMJXAsKzpUKETZdz9YU64", False),
    ]
    assert "".join(event.text for event in first if isinstance(event, Text)) == 'The file says "hello."\n\nPINEAPPLE'
    assert sum(isinstance(event, Text) for event in first) > 1
    assert "".join(event.text for event in second if isinstance(event, Text)) == 'It said "hello."\n\nPINEAPPLE'
    assert runner.session_id == CLAUDE_SESSION


def test_claude_model_and_effort_reach_every_turn(fake_cli, monkeypatch, tmp_path):
    runner = AgentRunner("claude", tmp_path, "sales", model="sonnet", effort="low")
    monkeypatch.setenv("FAKE_STREAM", str(FIXTURES / "claude" / "first.jsonl"))
    run_turn(runner, "Hi")
    monkeypatch.setenv("FAKE_STREAM", str(FIXTURES / "claude" / "resume.jsonl"))
    run_turn(runner, "Again")

    assert [call["argv"][-4:] for call in fake_cli()] == [["--model", "sonnet", "--effort", "low"]] * 2


def test_codex_model_and_effort_reach_every_turn(fake_cli, monkeypatch, tmp_path):
    runner = AgentRunner("codex", tmp_path, "sales", model="gpt-5.4", effort="minimal")
    monkeypatch.setenv("FAKE_STREAM", str(FIXTURES / "codex" / "first.jsonl"))
    run_turn(runner, "Hi")
    monkeypatch.setenv("FAKE_STREAM", str(FIXTURES / "codex" / "resume.jsonl"))
    run_turn(runner, "Again")

    settings = ["-c", 'model="gpt-5.4"', "-c", 'model_reasoning_effort="minimal"', "-"]
    assert [call["argv"][-5:] for call in fake_cli()] == [settings] * 2


def test_codex_first_turn_then_resume(fake_cli, monkeypatch, tmp_path):
    runner = AgentRunner("codex", tmp_path, "sales")
    monkeypatch.setenv("FAKE_MCP", MCP_SERVERS)
    monkeypatch.setenv("FAKE_STREAM", str(FIXTURES / "codex" / "first.jsonl"))
    first = run_turn(runner, "Read note.txt", 'Say "hi"')
    monkeypatch.setenv("FAKE_STREAM", str(FIXTURES / "codex" / "resume.jsonl"))
    second = run_turn(runner, "What did it say?", 'Say "hi"')

    first_call, second_call = fake_cli()
    assert first_call["argv"] == [
        "exec", "--json", "-s", "read-only", "--skip-git-repo-check", "-C", str(tmp_path),
        "-c", 'developer_instructions="Say \\"hi\\""', *MCP_OFF, "-",
    ]
    assert second_call["argv"] == [
        "exec", "resume", CODEX_THREAD, "--json", "--skip-git-repo-check", "-c", 'sandbox_mode="read-only"', *MCP_OFF, "-",
    ]
    assert first_call["stdin"] == "Read note.txt"
    assert first == [
        Session(CODEX_THREAD),
        Text("I’ll read note.txt. PINEAPPLE"),
        ToolStarted("item_1", "command_execution", "/bin/zsh -lc 'cat note.txt'"),
        ToolFinished("item_1", False),
        Text("\n\n"),
        Text("note.txt contains “hello.” PINEAPPLE"),
    ]
    assert second == [Session(CODEX_THREAD), Text("Contained “hello.” PINEAPPLE")]
    assert runner.session_id == CODEX_THREAD


def test_failed_exit_is_reported(fake_cli, monkeypatch, tmp_path):
    monkeypatch.setenv("FAKE_STREAM", str(FIXTURES / "codex" / "resume.jsonl"))
    monkeypatch.setenv("FAKE_EXIT", "3")
    events = run_turn(AgentRunner("codex", tmp_path, "sales"))
    assert events[-1] == Failed("`codex` exited with 3: ")


@pytest.mark.parametrize(
    ("servers", "message"),
    [
        ("not json", r"^`codex mcp list --json` failed, so its MCP servers cannot be turned off: $"),
        ('[{"name": "a.b", "enabled": true, "transport": {"type": "stdio"}}]', r"^The codex MCP server 'a.b' cannot be turned off.$"),
        ('[{"name": "ws", "enabled": true, "transport": {"type": "websocket"}}]', r"^The codex MCP server 'ws' cannot be turned off.$"),
    ],
    ids=["unreadable-list", "dotted-name", "unknown-transport"],
)
def test_codex_turn_fails_when_mcp_servers_cannot_be_turned_off(fake_cli, monkeypatch, tmp_path, servers, message):
    monkeypatch.setenv("FAKE_MCP", servers)
    monkeypatch.setenv("FAKE_STREAM", str(FIXTURES / "codex" / "resume.jsonl"))
    with pytest.raises(AgentError, match=message):
        run_turn(AgentRunner("codex", tmp_path, "sales"))

    assert not (tmp_path / "log.jsonl").exists()


def test_missing_executable(monkeypatch, tmp_path):
    monkeypatch.setenv("PATH", str(tmp_path))
    with pytest.raises(AgentError, match="^`codex` was not found on PATH.$"):
        run_turn(AgentRunner("codex", tmp_path, "sales"))


def test_second_turn_is_refused_while_running_and_stop_ends_it(fake_cli, monkeypatch, tmp_path):
    monkeypatch.setenv("FAKE_STREAM", str(FIXTURES / "codex" / "resume.jsonl"))
    monkeypatch.setenv("FAKE_SLEEP", "30")
    runner = AgentRunner("codex", tmp_path, "sales")

    async def scenario():
        events = []

        async def consume():
            async for event in runner.turn("Hi", "SYSTEM"):
                events.append(event)

        task = asyncio.create_task(consume())
        while not events:
            await asyncio.sleep(0.01)

        with pytest.raises(AgentError, match="^A turn is already running.$"):
            await anext(runner.turn("Again", "SYSTEM"))

        started = time.monotonic()
        await runner.stop()
        await task

        return events, time.monotonic() - started

    events, elapsed = asyncio.run(scenario())
    assert events == [Session(CODEX_THREAD), Text("Contained “hello.” PINEAPPLE")]
    assert elapsed < 3.0
    assert not runner.running
    assert len(fake_cli()) == 1
