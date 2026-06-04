from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Mapping
from datetime import date
from datetime import datetime
from datetime import time
from inspect import Parameter
from inspect import Signature
from pathlib import Path
from typing import Any


PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"
REQUIRED = object()


class LazyStaticAsset:
    def __init__(self, path: Path) -> None:
        self._path = path

    def __str__(self) -> str:
        try:
            return self._path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            msg = f"anylumino static asset is missing: {self._path}. Run `npm run build`."
            raise FileNotFoundError(msg) from exc


def static_asset(filename: str) -> Path | LazyStaticAsset:
    path = STATIC_DIR / filename
    if path.is_file():
        return path
    return LazyStaticAsset(path)


def json_value(value: Any) -> Any:
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, tuple):
        return [json_value(item) for item in value]
    if isinstance(value, list):
        return [json_value(item) for item in value]
    return value


def options_tuple(options: Iterable[Any] | None) -> tuple[Any, ...]:
    if options is None:
        return ()
    if isinstance(options, Mapping):
        return tuple((str(label), json_value(value)) for label, value in options.items())

    normalized = []
    for option in options:
        if isinstance(option, (list, tuple)) and len(option) == 2:
            label, value = option
            normalized.append((str(label), json_value(value)))
        else:
            normalized.append(json_value(option))
    return tuple(normalized)


def option_value(option: Any) -> Any:
    if isinstance(option, (list, tuple)) and len(option) == 2:
        return option[1]
    return option


def signature(
    parameters: list[tuple[str, object]],
    *,
    required_marker: object = REQUIRED,
) -> Signature:
    signature_params = []
    for name, default in parameters:
        if default is required_marker:
            signature_params.append(Parameter(name, Parameter.POSITIONAL_OR_KEYWORD))
        else:
            signature_params.append(Parameter(name, Parameter.POSITIONAL_OR_KEYWORD, default=default))
    return Signature(signature_params)


def doc(
    summary: str,
    parameters: list[tuple[str, object]],
    parameter_docs: Mapping[str, str],
    *,
    fallback: str,
    required_marker: object = REQUIRED,
) -> str:
    lines = [summary, "", "Parameters", "----------"]
    for name, default in parameters:
        qualifier = "required" if default is required_marker else "optional"
        lines.append(f"{name} : {qualifier}")
        lines.append(f"    {parameter_docs.get(name, fallback)}")
    return "\n".join(lines)


def document_control(
    cls: type[Any],
    summary: str,
    parameters: list[tuple[str, object]],
    parameter_docs: Mapping[str, str],
    *,
    fallback: str = "Control option.",
    required_marker: object = REQUIRED,
) -> None:
    cls.__signature__ = signature(parameters, required_marker=required_marker)  # type: ignore[attr-defined]
    cls.__doc__ = doc(
        summary,
        parameters,
        parameter_docs,
        fallback=fallback,
        required_marker=required_marker,
    )
