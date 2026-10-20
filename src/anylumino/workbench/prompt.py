"""The workbench system prompt: the OpenUI prompt for the catalog plus the callback contract."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from . import openui
from . import skill
from .catalog import library_spec
from .skill import Skill


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

CALLBACKS = """## Python callbacks

Interactive components run Python through `@Callback(handler, context?)`. Put the handlers in one
fenced block labeled `python`, next to the openui-lang block, as methods of one `App` subclass. Use
the `python` label for that block only; label any other code you show, such as a snippet for the
user, `text`.

```python
from anylumino.workbench import App


class SalesApp(App):
    def setup(self):
        self.ui.table.set_rows(self.sales.to_dict("records"))
        self.ui.region.items = ["All", *sorted(self.sales["region"].unique())]

    def on_run(self, event):
        region = self.ui.region.value or "All"
        self.ui.summary.text = f"Region: {region}"
```

- A handler is a method that takes `event`, an `Event` with `event.source` (the statement name of
  the component that fired), `event.value` (the new value for `on_change`, `None` for a button), and
  `event.context` (the second `@Callback` argument).
- `self.ui` is the generated UI, with one attribute per statement name. Inputs expose `.value`;
  Heading, Text, and Markdown expose `.text`; Button and Badge expose `.label`; Selector exposes
  `.items`; Table has `.set_rows(records)`. Statement names cannot be `app` or `widget`.
- The namespace listed below reaches the app as attributes, such as `self.sales`. There are no
  globals: read data only through `self`.
- An optional `setup(self)` runs once while the UI is built. Fill tables and selectors from
  namespace data there instead of copying the data into the program: you see only the shape and
  columns of data frames, not their rows.
- `self.ask_agent(message, context=None)` sends you a chat message from a handler.
- Do not name a method after an `App` member: `ui`, `agent`, `on_error`, `set_ui`, `call`, or
  `ask_agent`.
- Every handler named in `@Callback` must be a method. The python block always holds the complete
  class: omit the block when no handler changes, and when one changes, send the whole class. A UI
  without handlers needs no python block.
- Export puts the class in one module with the UI code, so bind the module names `UI`, `al`, `ax`,
  `go`, `Event`, and `View` only as the generated code does.
- A `Plot` is an empty Plotly `FigureWidget`; fill it in handlers inside
  `with self.ui.chart.batch_update():`. Use one `Plot` per chart.
- For one component per data item, declare an empty container, such as `cards = HBox([])`, and fill
  it in a handler with the Python constructors of the skill, by keyword:
  `self.ui.cards.widgets = [ax.Card(children=[ax.Text(text=n)]) for n in names]`.
- Keep state and data in the app: `$variables`, `Query`, `Mutation`, and `@Each` are not supported.
"""

COMPONENT_OPTIONS = f"""## Component options

Components whose signature ends with `options?` take an object of extra keyword options as their
last argument, for example `Table(rows, ["region"], {{sortable: true}})`. Before you use the options
of a component, look them up in the `{skill.NAME}` skill, or read `{skill.SKILL}/components/<Name>.md`.
An unknown option stops the reply from being applied.
"""

_cache: dict[str, str] = {}


async def system_prompt(namespace: Mapping[str, Any], skills: Sequence[Skill] = ()) -> str:
    """Return the full system prompt, with ``namespace`` and the notebook ``skills`` described for the agent."""
    sections = [await base_prompt(), COMPONENT_OPTIONS, CALLBACKS, namespace_summary(namespace)]

    return "\n\n".join([*sections, *([skills_summary(skills)] if skills else [])])


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

    lines = ["## Namespace", "", "The app gets these names as attributes, such as `self.<name>`; `Widget(name)` mounts the widgets among them:", ""]
    for name, value in namespace.items():
        kind = f"{type(value).__module__}.{type(value).__qualname__}"
        detail = ""
        shape = getattr(value, "shape", None)
        columns = getattr(value, "columns", None)
        dtypes = getattr(value, "dtypes", None)
        if shape is not None and columns is not None:
            if dtypes is not None and len(dtypes) == len(columns):
                described = ", ".join(f"`{column}` ({dtype})" for column, dtype in zip(columns, dtypes, strict=True))
            else:
                described = ", ".join(f"`{column}`" for column in columns)

            detail = f", shape {tuple(shape)}, columns {described}"

        lines.append(f"- `{name}`: `{kind}`{detail}")

    return "\n".join(lines)


def skills_summary(skills: Sequence[Skill]) -> str:
    """List the notebook skills by name, description, and path, so the agent loads one when needed."""
    lines = [
        "## Notebook skills",
        "",
        "These skills document libraries of this notebook that callbacks can import. Before you use one",
        "of their APIs, load its skill: with the Skill tool when you have it, otherwise read its SKILL.md",
        "and then the files it points to.",
        "",
    ]
    lines += [f"- `{entry.name}`: {entry.description} (`{entry.path / 'SKILL.md'}`)" for entry in skills]

    return "\n".join(lines)
