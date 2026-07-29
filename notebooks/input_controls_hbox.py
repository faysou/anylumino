# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # anylumino input controls
#
# Every Astryx input wrapper in one scrollable panel, each reporting its value to
# the status line below.

# %%
from __future__ import annotations

from typing import Any

import anylumino as al
import anylumino.astryx as ax


def describe_value(value: Any) -> str:
    if isinstance(value, bytes):
        return f"{len(value)} bytes"
    if isinstance(value, dict):
        return f"{len(value)} item(s)"
    if isinstance(value, (list, tuple)):
        return ", ".join(map(str, value)) or "empty"
    return str(value)


status = ax.Text("Change a control or press Apply to see its value here.")


# %%
controls = {
    "text": ax.TextInput(value="Iris", label="Text"),
    "textarea": ax.TextArea(value="Observation note", label="Area", rows=2),
    "password": ax.TextInput(value="secret", label="Password", input_type="password"),
    "int": ax.NumberInput(10, label="Int", integer_only=True),
    "bounded-int": ax.NumberInput(5, label="Bounded int", min=0, max=10, integer_only=True),
    "float": ax.NumberInput(1.25, label="Float", step=0.25),
    "bounded-float": ax.NumberInput(0.5, label="Bounded float", min=0.0, max=1.0, step=0.05),
    "int-slider": ax.Slider(25, label="Int slider", min=0, max=100, step=1, value_display="text"),
    "int-range": ax.Slider([20, 80], label="Int range", min=0, max=100, step=1),
    "float-slider": ax.Slider(0.25, label="Float slider", min=0.0, max=1.0, step=0.05),
    "float-range": ax.Slider([0.2, 0.8], label="Float range", min=0.0, max=1.0, step=0.05),
    # Astryx sliders step linearly, so LogSlider drives one in exponent space.
    "log-slider": ax.LogSlider(10.0, label="Log slider", base=10, min_exponent=0, max_exponent=3),
    "checkbox": ax.Checkbox(True, label="Checkbox"),
    "switch": ax.Switch(True, label="Switch"),
    "toggle": ax.ToggleButton(True, label="Toggle"),
    "toggle-buttons": ax.ToggleButtonGroup(["Low", "Medium", "High"], value="Medium", label="Toggles"),
    "segmented": ax.SegmentedControl(["Compact", "Standard"], value="Standard", label="Density"),
    "dropdown": ax.Selector(["Daily", "Weekly", "Monthly"], value="Weekly", label="Dropdown"),
    "combobox": ax.Typeahead(["Iris", "Daisy", "Lupine"], value="Iris", label="Combobox"),
    "search": ax.TextInput(value="greenhouse", label="Search", placeholder="Search data", clear=True),
    "radio": ax.RadioList(["Line", "Bar", "Area"], value="Line", label="Radio"),
    "list": ax.Selector(["Iris", "Daisy", "Lupine"], value="Iris", label="List", search=True),
    "checkbox-list": ax.CheckboxList(["Quotes", "Trades"], value=["Quotes"], label="Streams"),
    "multi": ax.MultiSelector(["Temperature", "Humidity", "CO2"], value=["Humidity"], label="Multi"),
    # Discrete option sliders report the option value, single or range.
    "selection": ax.SelectionSlider(["Low", "Medium", "High"], value="Medium", label="Selection", marks=True),
    "selection-range": ax.SelectionSlider(
        ["Mon", "Tue", "Wed", "Thu", "Fri"],
        value=["Tue", "Thu"],
        label="Sel range",
        marks=True,
    ),
    "date": ax.DateInput("2026-05-31", label="Date"),
    "datetime": ax.DateTimeInput("2026-05-31T09:30", label="Datetime"),
    "time": ax.TimeInput("09:30", label="Time"),
    "tags": ax.Tokenizer(["review", "field", "lab"], value=["review", "field"], label="Tags"),
    "ints": ax.TextInput(value="1, 2, 3", label="Ints"),
    "floats": ax.TextInput(value="1.5, 2.5", label="Floats"),
    "upload": ax.FileInput(label="Upload", mode="input"),
    "apply": ax.Button("Apply", variant="primary"),
    "valid": ax.FieldStatus("Valid", type="success"),
    "status-light": ax.StatusDot("Synced", variant="success", tooltip="Synced"),
    "badge": ax.Badge("Ready", variant="info"),
    "meter": ax.ProgressBar(68, label="Completion", variant="success", value_label=True),
    "link": ax.Link("Astryx docs", href="https://astryx.atmeta.com/components"),
    "divider": ax.Divider(),
}


# %%
def update_status(name: str, value: Any) -> None:
    if name == "password":
        status.text = "password changed: redacted"
    else:
        status.text = f"{name}: {describe_value(value)}"


for key, control in controls.items():
    control.observe(lambda change, key=key: update_status(key, change["new"]), names="value")

controls["apply"].on_click(lambda _button: update_status("apply", "clicked"))


# %%
panel = al.ScrollBox(
    {**controls, "status": status},
    spacing=10,
    width="100%",
    height=900,
    child_min_height=72,
)

panel

# %%
assert controls["log-slider"].component_name == "LogSlider"
assert controls["selection"].value == "Medium"
assert controls["selection-range"].value == ["Tue", "Thu"]
assert controls["int-range"].value == [20, 80]
assert controls["password"].props["type"] == "password"
assert controls["ints"].value == "1, 2, 3"
assert controls["floats"].value == "1.5, 2.5"

# %%
