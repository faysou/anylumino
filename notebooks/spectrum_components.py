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
# # anylumino Spectrum components
#
# This notebook focuses on controls rendered through Adobe Spectrum Web
# Components and shows how callbacks can update sibling widgets.

# %%
from __future__ import annotations

import anylumino.spectrum as sx

from anylumino import HBox
from anylumino import TextWidget
from anylumino import VBox


status = sx.StatusLight(value=True, description="Ready", variant="positive")
badge = sx.Badge(value="Idle", variant="informative", icon="InfoCircle")
meter = sx.Meter(value=35, description="Progress", variant="informative", readout=True)
log = TextWidget("Use the controls to update this panel.")


search = sx.SearchInput(value="iris", description="Search", placeholder="Search records")
dataset = sx.Dropdown(
    options=["Iris", "Daisy", "Lupine"],
    value="Iris",
    description="Dataset",
)
enabled = sx.Switch(value=True, description="Live updates")
pinned = sx.Checkbox(value=False, description="Pinned")
view_mode = sx.ToggleButtons(
    options=["Compact", "Standard", "Detailed"],
    value="Standard",
    description="View",
    icons=["ArrowDown", "Circle", "ArrowUp"],
)


def set_state(message: str, variant: str = "positive") -> None:
    status.variant = variant
    status.description = "Ready" if variant == "positive" else "Needs attention"
    badge.value = message
    badge.variant = "positive" if variant == "positive" else "negative"
    meter.value = min(100, meter.value + 15)
    log.value = f"{message}: {dataset.value}, {view_mode.value}, query={search.value!r}"


def apply_filters(_button: Button) -> None:
    set_state("Applied")


def reset_filters(_button: Button) -> None:
    search.value = ""
    dataset.value = "Iris"
    enabled.value = True
    pinned.value = False
    view_mode.value = "Standard"
    meter.value = 0
    set_state("Reset", "positive")


apply_button = sx.Button(
    description="Apply",
    icon="CheckmarkCircle",
    variant="accent",
    callbacks=[apply_filters],
)
reset_button = sx.Button(
    description="Reset",
    icon="RotateRight",
    variant="secondary",
    quiet=True,
    callbacks=[reset_filters],
)
favorite_button = sx.ToggleButton(
    value=False,
    description="Favorite",
    icon="Star",
    variant="secondary",
)
docs_link = sx.Link(
    "https://opensource.adobe.com/spectrum-web-components/",
    description="Spectrum docs",
)


for control in (search, dataset, enabled, pinned, view_mode, favorite_button):
    control.observe(lambda _change: set_state("Changed", "positive"), names="value")


summary = HBox(
    {
        "status": status,
        "badge": badge,
        "meter": meter,
        "docs": docs_link,
    },
    spacing=12,
    scroll=True,
    child_min_width=180,
    fit_content=True,
)

form = VBox(
    {
        "search": search,
        "dataset": dataset,
        "toggles": HBox(
            {
                "enabled": enabled,
                "pinned": pinned,
                "favorite": favorite_button,
            },
            spacing=12,
            scroll=True,
            child_min_width=170,
            fit_content=True,
        ),
        "view-mode": view_mode,
        "divider": sx.Divider(),
        "actions": HBox(
            {
                "apply": apply_button,
                "reset": reset_button,
            },
            spacing=8,
            scroll=True,
            child_min_width=120,
            fit_content=True,
        ),
        "log": log,
    },
    spacing=12,
    child_min_height=58,
    fit_content=True,
)


VBox(
    {
        "summary": summary,
        "form": form,
    },
    spacing=12,
    width="100%",
    height=540,
    fit_content=True,
)

# %%
