import json
import os
import shutil
import sys

import pytest


FAKE_CLI = f"""#!{sys.executable}
import json, os, sys, time
if sys.argv[1:3] == ["mcp", "list"]:
    sys.stdout.write(os.environ.get("FAKE_MCP", "[]"))
    sys.exit(0)
with open(os.environ["FAKE_LOG"], "a") as log:
    log.write(json.dumps({{"argv": sys.argv[1:], "stdin": sys.stdin.read(), "cwd": os.getcwd()}}) + "\\n")
sys.stdout.write(open(os.environ["FAKE_STREAM"]).read())
sys.stdout.flush()
time.sleep(float(os.environ.get("FAKE_SLEEP", "0")))
sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
"""


@pytest.fixture
def fake_cli(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("claude", "codex"):
        path = bin_dir / name
        path.write_text(FAKE_CLI)
        path.chmod(0o755)

    log = tmp_path / "log.jsonl"
    # Keep `node` reachable for the OpenUI tool; the fakes shadow any real agent CLI.
    node_dir = os.path.dirname(shutil.which("node") or "")
    monkeypatch.setenv("PATH", os.pathsep.join(filter(None, [str(bin_dir), node_dir])))
    monkeypatch.setenv("FAKE_LOG", str(log))

    def calls():
        return [json.loads(line) for line in log.read_text().splitlines()]

    return calls


@pytest.fixture
def agent_reply(fake_cli, tmp_path, monkeypatch):
    stream = tmp_path / "stream.jsonl"
    monkeypatch.setenv("FAKE_STREAM", str(stream))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))

    def set_reply(text):
        events = [
            {"type": "thread.started", "thread_id": "thread-1"},
            {"type": "item.completed", "item": {"id": "item_0", "type": "agent_message", "text": text}},
            {"type": "turn.completed"},
        ]
        stream.write_text("".join(json.dumps(event) + "\n" for event in events))

    set_reply.calls = fake_cli

    return set_reply
