from __future__ import annotations

from datetime import date
from datetime import datetime
from datetime import time
from typing import Any

import anywidget
import traitlets as t

from .common import ActivationCallbacks
from .common import json_value as _json_value
from .common import static_asset


class _NativeControlWidget(ActivationCallbacks, anywidget.AnyWidget):
    """Base class for browser-native anylumino controls.

    ``on_click`` runs for every value change and ``on_action`` also receives the
    new value. Both accept ``remove=True`` to unregister a callback.
    """

    _esm = static_asset("controls/native_control_widget.bundle.js")
    _css = static_asset("controls/native_control_widget.css")

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
        self._init_callbacks()
        super().__init__(**kwargs)
        self.observe(self._notify_value_change, names="value")
        self._register_callbacks(callbacks)


class DatePicker(_NativeControlWidget):
    """Browser-native date picker control.

    Parameters
    ----------
    value : date | str | None, default None
        Initial value and synchronized Python value.
    description : str, default ''
        Label shown above the control.
    disabled : bool, default False
        Whether user interaction is disabled.
    min : date | str | None, default None
        Minimum date value.
    max : date | str | None, default None
        Maximum date value.
    step : int | str | None, default None
        Native input step value.
    continuous_update : bool, default True
        Whether Python receives updates while the user edits the input.
    width : str, default ''
        CSS width for the control.
    """

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
    """Browser-native time picker with hour and minute popup controls.

    Parameters
    ----------
    value : time | str | None, default None
        Initial value and synchronized Python value.
    description : str, default ''
        Label shown above the control.
    disabled : bool, default False
        Whether user interaction is disabled.
    min : time | str | None, default None
        Minimum time value.
    max : time | str | None, default None
        Maximum time value.
    step : int | str | None, default None
        Native input step value.
    continuous_update : bool, default True
        Whether Python receives updates while the user edits the input.
    width : str, default ''
        CSS width for the control.
    """

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
    """Browser-native date and time picker control.

    Parameters
    ----------
    value : datetime | str | None, default None
        Initial value and synchronized Python value.
    description : str, default ''
        Label shown above the control.
    disabled : bool, default False
        Whether user interaction is disabled.
    min : datetime | str | None, default None
        Minimum date and time value.
    max : datetime | str | None, default None
        Maximum date and time value.
    step : int | str | None, default None
        Native input step value.
    continuous_update : bool, default True
        Whether Python receives updates while the user edits the input.
    width : str, default ''
        CSS width for the control.
    """

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


__all__ = ["DatePicker", "DatetimePicker", "TimePicker"]
