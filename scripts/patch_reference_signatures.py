from __future__ import annotations

import inspect
import re
from pathlib import Path

from anylumino import _controls


REFERENCE_DIR = Path("web/reference")


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
        r"```python\n(?P<display_name>[A-Za-z_][A-Za-z0-9_]*)\([^\n]*\)\n```",
        re.MULTILINE,
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


def _format_default(default: object) -> str:
    if default is inspect.Signature.empty:
        return "_required_"
    return f"`{default!r}`"


if __name__ == "__main__":
    main()
