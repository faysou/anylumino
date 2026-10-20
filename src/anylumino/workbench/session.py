"""Named workbench sessions saved as JSON under `~/.anylumino/sessions/`."""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


_NAME = re.compile(r"[A-Za-z0-9_-]+")


@dataclass
class SessionState:
    """What a workbench needs to restore a session. The UI code is derived, so it is not stored."""

    name: str
    agent: str
    cwd: str
    agent_session_id: str | None = None
    model: str | None = None
    effort: str | None = None
    skills: list[str] = field(default_factory=list)
    messages: list[dict[str, Any]] = field(default_factory=list)
    program: str = ""
    callbacks: str = ""
    updated_at: str = ""


def sessions_dir() -> Path:
    return Path.home() / ".anylumino" / "sessions"


def session_path(name: str) -> Path:
    """Return the file of session ``name``; names are limited to letters, digits, `_`, and `-`."""
    if not _NAME.fullmatch(name):
        raise ValueError(f"Invalid session name {name!r}: use letters, digits, '_', and '-'.")

    return sessions_dir() / f"{name}.json"


def save(state: SessionState) -> Path:
    """Write ``state`` atomically, stamping ``updated_at``, and return the file path."""
    path = session_path(state.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    state.updated_at = datetime.now(UTC).isoformat(timespec="seconds")
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(asdict(state), indent=2) + "\n")
    os.replace(temporary, path)

    return path


def load(name: str) -> SessionState | None:
    """Return the saved session ``name``, or `None` when there is none."""
    path = session_path(name)
    if not path.exists():
        return None

    return SessionState(**json.loads(path.read_text()))
