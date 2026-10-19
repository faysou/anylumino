"""The workbench system prompt: the OpenUI prompt for the catalog plus the callback contract."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from . import openui
from . import skill
from .catalog import library_spec


PREAMBLE = (
    "You build notebook UIs for the user. Answer in prose, and when the UI or its behavior "
    "should change, add fenced code as described below. The UI is written in openui-lang."
)

OPTIONS: dict[str, Any] = {
    "preamble": PREAMBLE,
    "inlineMode": True,
    "editMode": True,
    "toolCalls": False,
    "bindings": False,
}

SETUP = "setup"

CALLBACKS = f"""## Python callbacks

Interactive components run Python through `@Callback(handler, context?)`. Put every handler in one
fenced block labeled `python`, next to the openui-lang block. Use the `python` label for that block
only; label any other code you show, such as a snippet for the user, `text`.

```python
def {SETUP}(widgets):
    widgets["table"].set_rows(sales.to_dict("records"))
    widgets["region"].items = ["All", *sorted(sales["region"].unique())]


def on_run(event, widgets):
    region = widgets["region"].value or "All"
    widgets["summary"].text = f"Region: {{region}}"
```

- A handler takes `event` and `widgets`. `event` is a dict with `source` (the statement name of the
  component that fired), `value` (the new value for `on_change`, `None` for a button), and
  `context` (the second `@Callback` argument).
- `widgets` maps every statement name to its live widget. Inputs expose `.value`; Heading, Text,
  and Markdown expose `.text`; Button and Badge expose `.label`; Selector exposes `.items`; Table
  has `.set_rows(records)`.
- An optional `{SETUP}(widgets)` function runs once each time the UI is built. Fill tables and
  selectors from namespace data there instead of copying the data into the program: you see only
  the shape and columns of data frames, not their rows.
- `ask_agent(message, context=None)` sends a new chat message to you from a handler.
- Every handler named in `@Callback` must be defined. The python block always holds the complete
  set of handlers: omit the block when no handler changes, and when one changes, send them all.
- Handlers run in the notebook kernel with the namespace listed below as globals.
"""

COMPONENT_OPTIONS = f"""## Component options

Components whose signature ends with `options?` take an object of extra keyword options as their
last argument, for example `Table(rows, ["region"], {{sortable: true}})`. Before you use the options
of a component, look them up in the `{skill.NAME}` skill, or read `{skill.SKILL}/components/<Name>.md`.
An unknown option stops the reply from being applied.
"""

_cache: dict[str, str] = {}


async def system_prompt(namespace: Mapping[str, Any]) -> str:
    """Return the full system prompt, with ``namespace`` described for the agent."""
    return "\n\n".join([await base_prompt(), COMPONENT_OPTIONS, CALLBACKS, namespace_summary(namespace)])


async def base_prompt() -> str:
    """Return the OpenUI prompt for the catalog, generated once per catalog version."""
    key = hashlib.sha256(json.dumps([library_spec(), OPTIONS], sort_keys=True).encode()).hexdigest()
    if key not in _cache:
        _cache[key] = await openui.prompt(OPTIONS)
    return _cache[key]


def namespace_summary(namespace: Mapping[str, Any]) -> str:
    """Describe each namespace entry by name and type, with shape and columns for data frames."""
    if not namespace:
        return "## Namespace\n\nThe namespace is empty."
    lines = ["## Namespace", "", "Callbacks can read these names; `Widget(name)` mounts the widgets among them:", ""]
    for name, value in namespace.items():
        kind = f"{type(value).__module__}.{type(value).__qualname__}"
        detail = ""
        shape = getattr(value, "shape", None)
        columns = getattr(value, "columns", None)
        if shape is not None and columns is not None:
            detail = f", shape {tuple(shape)}, columns {[str(column) for column in columns]}"
        lines.append(f"- `{name}`: `{kind}`{detail}")
    return "\n".join(lines)
