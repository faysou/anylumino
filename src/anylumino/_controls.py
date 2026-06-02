from __future__ import annotations

from datetime import date
from datetime import datetime
from datetime import time
from inspect import Parameter
from inspect import Signature
from pathlib import Path
from typing import Any

import anywidget
import traitlets as t


PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"


def _load_static(filename: str) -> str:
    return (STATIC_DIR / filename).read_text()


def _json_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.replace(microsecond=0).isoformat()
    if isinstance(value, date | time):
        return value.isoformat()
    return value


class _NativeControlWidget(anywidget.AnyWidget):
    """Base class for browser-native anylumino controls."""

    _esm = _load_static("native_control_widget.bundle.js")
    _css = _load_static("native_control_widget.css")

    control_family = t.Unicode("native").tag(sync=True)
    control_kind = t.Unicode("date").tag(sync=True)
    value = t.Any(None, allow_none=True).tag(sync=True)
    description = t.Unicode("").tag(sync=True)
    disabled = t.Bool(False).tag(sync=True)
    continuous_update = t.Bool(True).tag(sync=True)
    min = t.Any(None, allow_none=True).tag(sync=True)
    max = t.Any(None, allow_none=True).tag(sync=True)
    step = t.Any(None, allow_none=True).tag(sync=True)
    width = t.Unicode("").tag(sync=True)

    def __init__(self, **kwargs: Any) -> None:
        callbacks = kwargs.pop("callbacks", None)
        super().__init__(**kwargs)
        self._callbacks: list[Any] = []
        if callbacks is not None:
            for callback in callbacks:
                self.observe(lambda _change, callback=callback: callback(self), names="value")
                self._callbacks.append(callback)


class DatePicker(_NativeControlWidget):
    """Browser-native date picker control."""

    def __init__(
        self,
        value: date | str | None = None,
        *,
        description: str = "",
        disabled: bool = False,
        min: date | str | None = None,
        max: date | str | None = None,
        step: int | str | None = None,
        continuous_update: bool = True,
        width: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            control_kind="date",
            value=_json_value(value),
            description=description,
            disabled=disabled,
            min=_json_value(min),
            max=_json_value(max),
            step=step,
            continuous_update=continuous_update,
            width=width,
            **kwargs,
        )


class TimePicker(DatePicker):
    """Browser-native time picker with hour and minute popup controls."""

    def __init__(
        self,
        value: time | str | None = None,
        *,
        description: str = "",
        disabled: bool = False,
        min: time | str | None = None,
        max: time | str | None = None,
        step: int | str | None = None,
        continuous_update: bool = True,
        width: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            description=description,
            disabled=disabled,
            min=min,
            max=max,
            step=step,
            continuous_update=continuous_update,
            width=width,
            **kwargs,
        )
        self.control_kind = "time"


class DatetimePicker(DatePicker):
    """Browser-native date and time picker control."""

    def __init__(
        self,
        value: datetime | str | None = None,
        *,
        description: str = "",
        disabled: bool = False,
        min: datetime | str | None = None,
        max: datetime | str | None = None,
        step: int | str | None = None,
        continuous_update: bool = True,
        width: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            value=value,
            description=description,
            disabled=disabled,
            min=min,
            max=max,
            step=step,
            continuous_update=continuous_update,
            width=width,
            **kwargs,
        )
        self.control_kind = "datetime"


def _parameter(name: str, default: Any) -> Parameter:
    return Parameter(name, Parameter.POSITIONAL_OR_KEYWORD, default=default)


def _document_control(cls: type[Any], summary: str, params: list[tuple[str, Any]]) -> None:
    signature_params = [_parameter(name, default) for name, default in params]
    cls.__signature__ = Signature(signature_params)  # type: ignore[attr-defined]
    arguments = "\n".join(
        f"{name} : optional\n    {_CONTROL_PARAM_DOCS.get(name, 'Control option.')}"
        for name, _default in params
    )
    cls.__doc__ = f"""{summary}

    Parameters
    ----------
{arguments}
    """


_CONTROL_PARAM_DOCS = {
    "continuous_update": "Whether Python receives updates while the user edits the input.",
    "description": "Label shown above the control.",
    "disabled": "Whether user interaction is disabled.",
    "max": "Maximum date, time, or datetime value.",
    "min": "Minimum date, time, or datetime value.",
    "step": "Native input step value.",
    "value": "Initial value and synced Python value.",
    "width": "CSS width for the control.",
}


for _cls, _summary, _params in [
    (
        DatePicker,
        "Browser-native date picker control.",
        [
            ("value", None),
            ("description", ""),
            ("disabled", False),
            ("min", None),
            ("max", None),
            ("step", None),
            ("continuous_update", True),
            ("width", ""),
        ],
    ),
    (
        TimePicker,
        "Browser-native time picker control.",
        [
            ("value", None),
            ("description", ""),
            ("disabled", False),
            ("min", None),
            ("max", None),
            ("step", None),
            ("continuous_update", True),
            ("width", ""),
        ],
    ),
    (
        DatetimePicker,
        "Browser-native datetime picker control.",
        [
            ("value", None),
            ("description", ""),
            ("disabled", False),
            ("min", None),
            ("max", None),
            ("step", None),
            ("continuous_update", True),
            ("width", ""),
        ],
    ),
]:
    _document_control(_cls, _summary, _params)


__all__ = ["DatePicker", "DatetimePicker", "TimePicker"]
