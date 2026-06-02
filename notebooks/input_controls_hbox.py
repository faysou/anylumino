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
# This notebook shows native anylumino input controls inside one scrollable
# Lumino `VBox`.

# %%
from __future__ import annotations

from datetime import date
from datetime import datetime
from datetime import time
from datetime import timezone
from typing import Any

from anylumino import (
    Badge,
    BoundedFloatText,
    BoundedIntText,
    Button,
    Checkbox,
    ColorPicker,
    ColorsInput,
    Combobox,
    DatePicker,
    DatetimePicker,
    Divider,
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
    Link,
    ListBox,
    Meter,
    MultiSelect,
    PasswordInput,
    Play,
    RadioButtons,
    ScrollBox,
    SearchInput,
    SelectionRangeSlider,
    SelectionSlider,
    StatusLight,
    Switch,
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
    "text": TextInput(value="Iris", description="Text"),
    "textarea": TextArea(value="Observation note", description="Area"),
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
    "switch": Switch(value=True, description="Switch"),
    "toggle": ToggleButton(value=True, description="Toggle", icon="CheckmarkCircle"),
    "toggle-buttons": ToggleButtons(
        options=["Low", "Medium", "High"],
        value="Medium",
        description="Toggles",
        icons=["ArrowDown", "Circle", "ArrowUp"],
    ),
    "dropdown": Dropdown(options=["Daily", "Weekly", "Monthly"], value="Weekly", description="Dropdown"),
    "combobox": Combobox(options=["Iris", "Daisy", "Lupine"], value="Iris", description="Combobox"),
    "search": SearchInput(value="greenhouse", description="Search", placeholder="Search data"),
    "radio": RadioButtons(options=["Line", "Bar", "Area"], value="Line", description="Radio"),
    "list": ListBox(options=["Iris", "Daisy", "Lupine"], value="Iris", description="List"),
    "multi": MultiSelect(options=["Temperature", "Humidity", "CO2"], value=("Humidity",), description="Multi"),
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
        value=["review", "field"],
        allowed_tags=["review", "field", "lab"],
        description="Tags",
    ),
    "colors": ColorsInput(value=["red", "#0ea5e9"], description="Colors"),
    "ints": IntsInput(value=[1, 2, 3], description="Ints"),
    "floats": FloatsInput(value=[1.5, 2.5], description="Floats"),
    "upload": FileUpload(description="Upload"),
    "play": Play(value=0, min=0, max=10, interval=250, description="Play"),
    "apply": Button(description="Apply", variant="accent", icon="CheckmarkCircle"),
    "valid": Valid(value=True, description="Valid"),
    "status-light": StatusLight(value=True, description="Synced", variant="positive"),
    "badge": Badge(value="Ready", variant="informative", icon="InfoCircle"),
    "meter": Meter(value=68, description="Completion", variant="positive", readout=True),
    "link": Link("https://opensource.adobe.com/spectrum-web-components/", description="Spectrum docs"),
    "divider": Divider(),
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
    spacing=10,
    width="100%",
    height=900,
    child_min_height=72,
)

controls_vbox

# %%
status

# %%
