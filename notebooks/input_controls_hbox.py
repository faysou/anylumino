# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # anylumino input controls ScrollBox
#
# This notebook shows the ipywidgets input controls exported by `anylumino`
# inside one scrollable Lumino `VBox`.

# %%
from __future__ import annotations

from datetime import date
from datetime import datetime
from datetime import time
from datetime import timezone
from typing import Any

from anylumino import (
    BoundedFloatText,
    BoundedIntText,
    Button,
    Checkbox,
    ColorPicker,
    ColorsInput,
    Combobox,
    DatePicker,
    DatetimePicker,
    Dropdown,
    FileUpload,
    FloatLogSlider,
    FloatRangeSlider,
    FloatSlider,
    FloatText,
    FloatsInput,
    IntRangeSlider,
    IntSlider,
    IntText,
    IntsInput,
    ListBox,
    MultiSelect,
    PasswordInput,
    Play,
    RadioButtons,
    ScrollBox,
    SelectionRangeSlider,
    SelectionSlider,
    TagsInput,
    TextArea,
    TextInput,
    TextWidget,
    TimePicker,
    ToggleButton,
    ToggleButtons,
    Valid,
)


def describe_value(value: Any) -> str:
    if isinstance(value, bytes):
        return f"{len(value)} bytes"
    if isinstance(value, dict):
        return f"{len(value)} item(s)"
    if isinstance(value, (list, tuple)):
        return ", ".join(map(str, value)) or "empty"
    return str(value)


status = TextWidget("Change a control or press Apply to see its value here.")


controls = {
    "text": TextInput(value="AAPL", description="Text"),
    "textarea": TextArea(value="Watchlist note", description="Area"),
    "password": PasswordInput(value="secret", description="Password"),
    "int": IntText(value=10, description="Int"),
    "bounded-int": BoundedIntText(value=5, min=0, max=10, description="Bounded int"),
    "float": FloatText(value=1.25, description="Float"),
    "bounded-float": BoundedFloatText(value=0.5, min=0.0, max=1.0, description="Bounded float"),
    "int-slider": IntSlider(value=25, min=0, max=100, description="Int slider"),
    "int-range": IntRangeSlider(value=[20, 80], min=0, max=100, description="Int range"),
    "float-slider": FloatSlider(value=0.25, min=0.0, max=1.0, step=0.05, description="Float slider"),
    "float-range": FloatRangeSlider(value=[0.2, 0.8], min=0.0, max=1.0, step=0.05, description="Float range"),
    "log-slider": FloatLogSlider(value=10.0, base=10, min=0, max=3, description="Log slider"),
    "checkbox": Checkbox(value=True, description="Checkbox"),
    "toggle": ToggleButton(value=True, description="Toggle"),
    "toggle-buttons": ToggleButtons(options=["Buy", "Hold", "Sell"], value="Hold", description="Toggles"),
    "dropdown": Dropdown(options=["1m", "5m", "1h"], value="5m", description="Dropdown"),
    "combobox": Combobox(options=["AAPL", "MSFT", "NVDA"], value="AAPL", description="Combobox"),
    "radio": RadioButtons(options=["Line", "Candle", "Area"], value="Candle", description="Radio"),
    "list": ListBox(options=["AAPL", "MSFT", "NVDA"], value="AAPL", description="List"),
    "multi": MultiSelect(options=["Volume", "SMA", "EMA"], value=("SMA",), description="Multi"),
    "selection": SelectionSlider(options=["Low", "Medium", "High"], value="Medium", description="Selection"),
    "selection-range": SelectionRangeSlider(
        options=["Mon", "Tue", "Wed", "Thu", "Fri"],
        index=(1, 3),
        description="Sel range",
    ),
    "color": ColorPicker(value="#0ea5e9", description="Color"),
    "date": DatePicker(value=date(2026, 5, 31), description="Date"),
    "datetime": DatetimePicker(
        value=datetime(2026, 5, 31, 9, 30, tzinfo=timezone.utc),
        description="Datetime",
    ),
    "time": TimePicker(value=time(9, 30), description="Time"),
    "tags": TagsInput(
        value=["breakout", "watch"],
        allowed_tags=["breakout", "watch", "risk"],
        description="Tags",
    ),
    "colors": ColorsInput(value=["red", "#0ea5e9"], description="Colors"),
    "ints": IntsInput(value=[1, 2, 3], description="Ints"),
    "floats": FloatsInput(value=[1.5, 2.5], description="Floats"),
    "upload": FileUpload(description="Upload"),
    "play": Play(value=0, min=0, max=10, interval=250, description="Play"),
    "apply": Button(description="Apply", button_style="primary"),
    "valid": Valid(value=True, description="Valid"),
}


def update_status(name: str, value: Any) -> None:
    if name == "password":
        status.text = "password changed: redacted"
    else:
        status.text = f"{name}: {describe_value(value)}"


for key, control in controls.items():
    if hasattr(control, "observe"):
        control.observe(
            lambda change, key=key: update_status(key, change["new"]),
            names="value",
        )


controls["apply"].on_click(lambda _button: update_status("apply", "clicked"))


controls_vbox = ScrollBox(
    controls,
    spacing=6,
    stretches=[1] * len(controls),
    width="100%",
    height=640,
)

controls_vbox

# %%
status
