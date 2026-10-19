import json

import pytest

from anylumino.workbench import session
from anylumino.workbench.session import SessionState


def test_session_round_trips_every_field(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    state = SessionState(
        name="sales-q3",
        agent="codex",
        cwd="/work",
        agent_session_id="thread-1",
        messages=[{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello", "status": "sent"}],
        program='root = VBox([title])\ntitle = Heading("Sales")',
        callbacks="def on_run(event, widgets):\n    pass\n",
    )
    path = session.save(state)

    assert path == tmp_path / ".anylumino" / "sessions" / "sales-q3.json"
    assert not path.with_suffix(".json.tmp").exists()
    saved = json.loads(path.read_text())
    assert saved == {
        "name": "sales-q3",
        "agent": "codex",
        "cwd": "/work",
        "agent_session_id": "thread-1",
        "messages": [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello", "status": "sent"}],
        "program": 'root = VBox([title])\ntitle = Heading("Sales")',
        "callbacks": "def on_run(event, widgets):\n    pass\n",
        "updated_at": state.updated_at,
    }
    assert len(state.updated_at) == len("2026-10-18T16:00:00+00:00")
    assert session.load("sales-q3") == state


def test_missing_session_loads_as_none(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    assert session.load("absent") is None


@pytest.mark.parametrize("name", ["../x", "a/b", "", "with space"])
def test_session_names_cannot_escape_the_directory(name):
    with pytest.raises(ValueError, match="^Invalid session name"):
        session.session_path(name)
