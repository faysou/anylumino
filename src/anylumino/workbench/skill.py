"""The agent skill that documents each catalog component's options, generated from the catalog.

The files live in a Claude Code plugin directory inside the package, so `claude`
loads the skill with ``--plugin-dir`` and `codex` reads the same files by path.
Run ``make workbench-skill`` after changing the catalog or a wrapper's keywords.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .catalog import COMPONENTS, Component, type_name


NAME = "openui-components"
PLUGIN = Path(__file__).parent / "plugin"
SKILL = PLUGIN / "skills" / NAME
DESCRIPTION = (
    "Options and Python constructors of the anylumino OpenUI components. Use before you pass an options "
    "object to a component in an openui-lang program, or build a component's widget in Python."
)


def files() -> dict[str, str]:
    """Return the plugin files by path relative to `PLUGIN`."""
    manifest = {"name": "anylumino", "description": "anylumino workbench skills", "version": "1.0.0"}
    result = {".claude-plugin/plugin.json": json.dumps(manifest, indent=2) + "\n", f"skills/{NAME}/SKILL.md": _skill()}
    for component in COMPONENTS:
        if component.module:
            result[f"skills/{NAME}/components/{component.name}.md"] = _component(component)

    return result


def write() -> None:
    """Write the plugin files and remove component files that no longer have options."""
    expected = files()
    for path in (SKILL / "components").glob("*.md"):
        if str(path.relative_to(PLUGIN)) not in expected:
            path.unlink()

    for relative, text in expected.items():
        path = PLUGIN / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def _skill() -> str:
    rows = "\n".join(
        f"| `{component.name}` | [components/{component.name}.md](components/{component.name}.md) |"
        for component in COMPONENTS
        if component.module
    )

    return f"""---
name: {NAME}
description: {DESCRIPTION}
---

# OpenUI component options

Most components below take an optional `options` object as their last argument. Its keys are extra
keyword options of the anylumino widget, for example:

```openui-lang
table = Table(rows, ["region", "revenue"], {{sortable: true, density: "compact"}})
```

Read the component's file before you use its options. Each file lists the option names, types,
and meanings. Option values must be literals. An unknown option or a value of the wrong type stops
the workbench from applying the reply.

Each file also gives the Python constructor that builds the component's widget, for callbacks that
fill a container in Python. Pass the arguments by keyword: the Python positional order differs from
the OpenUI one.

| Component | File |
| --------- | ---- |
{rows}
"""


def _component(component: Component) -> str:
    keywords = [
        f"{prop.keyword}=..." for prop in component.props if prop.kind not in ("action", "options")
    ] + [f"{key}={value!r}" for key, value in component.fixed]
    text = f"""# {component.name}

{component.description}.

In Python: `{component.factory}({", ".join(keywords)})`{", plus any option below as a keyword" if component.options else ""}.
"""
    if not component.options:
        return text

    rows = "\n".join(
        f"| `{name}` | `{_markdown(type_name(schema))}` | {_markdown(schema['description']) or 'Not documented.'} |"
        for name, schema in component.options.items()
    )

    return f"""{text}
## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
{rows}
"""


def _markdown(text: Any) -> str:
    return str(text).replace("``", "`").replace("|", "\\|")

