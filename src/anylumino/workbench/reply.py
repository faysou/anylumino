"""Split an agent reply into chat prose, an OpenUI program, and Python callbacks."""

from __future__ import annotations

import re
from dataclasses import dataclass


_FENCE = re.compile(r"^```[ \t]*([\w-]*)[ \t]*\n(.*?)^```[ \t]*$\n?", re.MULTILINE | re.DOTALL)
_PROGRAM_LABELS = ("openui", "openui-lang")


class ReplyError(ValueError):
    """The reply holds more than one block of the same kind."""


@dataclass(frozen=True)
class Reply:
    prose: str
    program: str | None
    callbacks: str | None


def split_reply(text: str) -> Reply:
    """Return the prose and the optional `openui` and `python` blocks of ``text``."""
    program: list[str] = []
    callbacks: list[str] = []

    def take(match: re.Match[str]) -> str:
        label, body = match.group(1).lower(), match.group(2)
        if label in _PROGRAM_LABELS:
            program.append(body)
        elif label == "python":
            callbacks.append(body)
        else:
            return match.group(0)
        return "\n"

    prose = _FENCE.sub(take, text)
    for blocks, label in ((program, "openui"), (callbacks, "python")):
        if len(blocks) > 1:
            raise ReplyError(f"The reply has {len(blocks)} `{label}` blocks; send at most one.")
    return Reply(
        re.sub(r"\n{3,}", "\n\n", prose).strip(),
        program[0].rstrip("\n") if program else None,
        callbacks[0] if callbacks else None,
    )
