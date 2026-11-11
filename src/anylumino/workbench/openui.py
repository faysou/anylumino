"""Parse, merge, and describe OpenUI Lang programs with the bundled `@openuidev/lang-core` tool."""

from __future__ import annotations

import asyncio
import json
import os
import shutil
from collections.abc import Sequence
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

from .catalog import COMPONENTS, Component, library_spec


TOOL = Path(__file__).resolve().parent.parent / "static" / "openui" / "openui_tool.bundle.mjs"


class OpenUIError(RuntimeError):
    """The OpenUI tool could not run or rejected the request."""


@dataclass(frozen=True)
class ParseResult:
    """A parsed program: its evaluated tree and what the parser reported about it.

    ``unresolved`` lists names the program uses without defining them; such a
    program does not apply.
    """

    root: dict[str, Any] | None
    errors: list[dict[str, Any]]
    unresolved: list[str]
    orphans: list[str]
    incomplete: bool
    statements: list[str]
    states: list[str]
    queries: list[str]
    mutations: list[str]


async def parse(program: str, components: Sequence[Component] = COMPONENTS) -> ParseResult:
    """Return the evaluated tree, errors, and statement names of ``program`` for the ``components`` catalog.

    Raises
    ------
    OpenUIError
        If the tool cannot run, or its response lacks a field of `ParseResult`.
    """
    response = await run_tool({"command": "parse", "program": program, "library": library_spec(components)})
    missing = [field.name for field in fields(ParseResult) if field.name not in response]
    if missing:
        raise OpenUIError(f"The OpenUI tool response lacks {', '.join(missing)}.")

    return ParseResult(**{field.name: response[field.name] for field in fields(ParseResult)})


async def merge(current: str, patch: str) -> str:
    """Merge ``patch`` into ``current`` by statement name, as OpenUI edit mode does."""

    return (await run_tool({"command": "merge", "current": current, "patch": patch}))["program"]


async def prompt(options: dict[str, Any], components: Sequence[Component] = COMPONENTS) -> str:
    """Return the OpenUI system prompt for the ``components`` catalog with the given prompt options."""

    return (await run_tool({"command": "prompt", "library": library_spec(components), "options": options}))["prompt"]


async def run_tool(request: dict[str, Any]) -> dict[str, Any]:
    """Send one request to the bundled tool and return its JSON response."""
    node = shutil.which("node")
    if node is None:
        raise OpenUIError("The workbench needs `node` on PATH to parse OpenUI programs.")

    process = await asyncio.create_subprocess_exec(
        node,
        str(TOOL),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={**os.environ, "OPENUI_TELEMETRY_DISABLED": "1"},
    )
    stdout, stderr = await process.communicate(json.dumps(request).encode())
    if process.returncode != 0:
        raise OpenUIError(f"OpenUI tool failed ({process.returncode}): {stderr.decode().strip()}")

    return json.loads(stdout)
