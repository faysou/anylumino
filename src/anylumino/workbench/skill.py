"""The workbench's agent skills: the built-in component skill and the notebook's own skill folders.

The built-in skill documents each catalog component and is generated from the
catalog. Its files live in a Claude Code plugin directory inside the package, so
`claude` loads it with ``--plugin-dir`` and `codex` reads the same files by path.
Run ``make workbench-skill`` after changing the catalog or a wrapper's keywords.

A notebook skill is a folder with a ``SKILL.md`` whose front matter gives its
``name`` and ``description``, in the Claude Code skill format, such as the API
of a private charting library. A ``components.py`` in the folder can add OpenUI
components for the library's widgets, so programs can lay them out like the
built-in ones.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .catalog import COMPONENTS, Component, PropKind, type_name


NAME = "openui-components"
PLUGIN = Path(__file__).parent / "plugin"
SKILL = PLUGIN / "skills" / NAME
DESCRIPTION = (
    "Options and Python constructors of the anylumino OpenUI components. Use before you pass an options "
    "object to a component in an openui-lang program, or build a component's widget in Python."
)


@dataclass(frozen=True)
class Skill:
    """A notebook skill folder: the name and description from its ``SKILL.md`` front matter, and its path.

    ``components`` are the OpenUI components its ``components.py`` defines,
    in a ``COMPONENTS`` sequence of `Component`; empty without that file.
    """

    name: str
    description: str
    path: Path
    components: tuple[Component, ...] = ()


def read_skill(folder: str | Path) -> Skill:
    """Read the ``SKILL.md`` front matter of ``folder``.

    Raises
    ------
    ValueError
        If ``folder`` has no ``SKILL.md``, its front matter lacks ``name`` or
        ``description``, or the name is not lowercase letters, digits, and ``-``.
    """
    path = Path(folder).expanduser().resolve()
    manifest = path / "SKILL.md"
    if not manifest.is_file():
        raise ValueError(f"{path} is not a skill folder: it has no SKILL.md")

    match = re.match(r"---\n(.*?)\n---\n", manifest.read_text(), re.DOTALL)
    fields = {}
    for line in match.group(1).splitlines() if match else []:
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip("\"'")

    name, description = fields.get("name", ""), fields.get("description", "")
    if not name or not description:
        raise ValueError(f"{manifest} needs front matter with a name and a description")

    if not re.fullmatch(r"[a-z0-9-]+", name):
        raise ValueError(f"{manifest}: the skill name {name!r} must use lowercase letters, digits, and '-'")

    return Skill(name, description, path, skill_components(path / "components.py"))


def skill_components(path: Path) -> tuple[Component, ...]:
    """Return the ``COMPONENTS`` that the skill file ``path`` defines, or none when it does not exist.

    Raises
    ------
    ValueError
        If the file does not define ``COMPONENTS`` as a sequence of `Component`.
    """
    if not path.is_file():
        return ()

    scope: dict[str, Any] = {"__name__": f"anylumino_skill_{path.parent.name.replace('-', '_')}"}
    exec(compile(path.read_text(), str(path), "exec"), scope)
    components = scope.get("COMPONENTS")
    if not isinstance(components, (list, tuple)) or not all(isinstance(item, Component) for item in components):
        raise ValueError(f"{path} must define COMPONENTS as a sequence of anylumino.workbench.catalog.Component")

    return tuple(components)


def write_plugin(skills: Sequence[Skill], directory: Path) -> Path:
    """Write a Claude Code plugin into ``directory`` that links each of ``skills``, and return it.

    The links keep a skill's later edits visible to the next turn.
    """
    (directory / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    manifest = {"name": "notebook", "description": "Skills of this notebook", "version": "1.0.0"}
    (directory / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (directory / "skills").mkdir(exist_ok=True)
    for skill in skills:
        (directory / "skills" / skill.name).symlink_to(skill.path, target_is_directory=True)

    return directory


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
        f"{prop.keyword}=..." for prop in component.props if prop.kind not in (PropKind.ACTION, PropKind.OPTIONS)
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

