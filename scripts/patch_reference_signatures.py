from __future__ import annotations

import inspect
import re
from pathlib import Path

from anylumino import _controls


REFERENCE_DIR = Path("web/reference")
REFERENCE_NOTES = {
    "TimePicker": """The frontend renders a native time input with an anylumino popup picker. The
popup shows hours and minutes in separate columns, so users can pick any minute
value instead of being limited to fixed 15-minute increments.

Python `datetime.time` values are accepted and serialized with `isoformat()`
before syncing to the frontend.""",
    "DatetimePicker": """The frontend renders separate date and time inputs. The time input uses the
same anylumino hour/minute popup as `TimePicker`, so users can pick any minute
value instead of being limited to fixed 15-minute increments.

Python `datetime.datetime` values are accepted and serialized with
`isoformat()` before syncing to the frontend.""",
}
PARAMETER_OVERRIDES = {
    ("TimePicker", "value"): (
        "`datetime.time`, `str`, or `None`",
        "Initial value and synced Python value. Strings should use `HH:MM` or another browser-compatible time value.",
    ),
    ("DatetimePicker", "value"): (
        "`datetime.datetime`, `str`, or `None`",
        "Initial value and synced Python value. Strings should use an ISO datetime value compatible with browser date and time inputs.",
    ),
}


def main() -> None:
    signatures = _control_signatures()
    for page in REFERENCE_DIR.glob("*.qmd"):
        name = page.stem
        signature = signatures.get(name)
        if signature is None:
            continue

        text = page.read_text()
        text = _replace_signature(text, name, signature)
        text = _replace_parameter_defaults(text, signature)
        text = _insert_reference_note(text, name)
        text = _replace_parameter_overrides(text, name)
        page.write_text(text)


def _control_signatures() -> dict[str, inspect.Signature]:
    signatures = {}
    for name in _controls.__all__:
        obj = getattr(_controls, name)
        signature = getattr(obj, "__signature__", None)
        if signature is not None:
            signatures[name] = signature
    return signatures


def _replace_signature(text: str, name: str, signature: inspect.Signature) -> str:
    pattern = re.compile(
        r"```python\n(?P<display_name>[A-Za-z_][A-Za-z0-9_]*)\([\s\S]*?\)\n```",
    )

    def replace(match: re.Match[str]) -> str:
        display_name = match.group("display_name")
        return _render_signature(display_name or name, signature)

    return pattern.sub(replace, text, count=1)


def _render_signature(name: str, signature: inspect.Signature) -> str:
    parameters = [
        _render_parameter(param_name, parameter)
        for param_name, parameter in signature.parameters.items()
    ]
    if not parameters:
        return f"```python\n{name}()\n```"

    lines = ["```python", f"{name}("]
    lines.extend(f"    {parameter}," for parameter in parameters)
    lines.extend([")", "```"])
    return "\n".join(lines)


def _render_parameter(name: str, parameter: inspect.Parameter) -> str:
    if parameter.default is inspect.Signature.empty:
        return name
    return f"{name}={parameter.default!r}"


def _replace_parameter_defaults(text: str, signature: inspect.Signature) -> str:
    defaults = {
        name: _format_default(parameter.default)
        for name, parameter in signature.parameters.items()
    }
    lines = text.splitlines()
    in_parameters = False
    patched = []

    for line in lines:
        if line.startswith("## Parameters"):
            in_parameters = True
        elif in_parameters and line.startswith("## "):
            in_parameters = False

        if in_parameters and line.startswith("|"):
            line = _replace_parameter_row_default(line, defaults)

        patched.append(line)

    return "\n".join(patched) + "\n"


def _replace_parameter_row_default(line: str, defaults: dict[str, str]) -> str:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if len(cells) != 4:
        return line

    name, type_name, description, default = cells
    if name not in defaults:
        return line

    return f"| {name} | {type_name} | {description} | {defaults[name]} |"


def _insert_reference_note(text: str, name: str) -> str:
    note = REFERENCE_NOTES.get(name)
    if note is None or note in text:
        return text
    marker = "\n## Parameters"
    if marker not in text:
        return text
    before, after = text.split(marker, 1)
    return f"{before.rstrip()}\n\n{note}\n{marker}{after}"


def _replace_parameter_overrides(text: str, page_name: str) -> str:
    lines = text.splitlines()
    patched = []
    in_parameters = False

    for line in lines:
        if line.startswith("## Parameters"):
            in_parameters = True
        elif in_parameters and line.startswith("## "):
            in_parameters = False

        if in_parameters and line.startswith("|"):
            line = _replace_parameter_row_override(line, page_name)

        patched.append(line)

    return "\n".join(patched) + "\n"


def _replace_parameter_row_override(line: str, page_name: str) -> str:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if len(cells) != 4:
        return line

    name, type_name, description, default = cells
    override = PARAMETER_OVERRIDES.get((page_name, name))
    if override is None:
        return line

    type_name, description = override
    return f"| {name} | {type_name} | {description} | {default} |"


def _format_default(default: object) -> str:
    if default is inspect.Signature.empty:
        return "_required_"
    return f"`{default!r}`"


if __name__ == "__main__":
    main()
