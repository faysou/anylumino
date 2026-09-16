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
# # Astryx layout panels
#
# The `anylumino.astryx` layout panels mirror the Lumino layout widgets with
# Astryx styling and the same keyed child API. This notebook shows each panel
# with Python-driven state changes, so run it top to bottom and watch the
# outputs update.

# %%
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

import anylumino.astryx as ax


def price_figure(seed: int, title: str) -> go.FigureWidget:
    rng = np.random.default_rng(seed)
    prices = 100 + rng.normal(0, 1, 120).cumsum()
    figure = go.FigureWidget(data=[go.Scatter(y=prices, mode="lines", name=title)])
    figure.update_layout(title=title, height=240, margin={"t": 40, "b": 30, "l": 40, "r": 20})
    return figure


status = ax.Text("Ready", text_type="supporting", color="secondary")

# %% [markdown]
# ## TabPanel
#
# One child per tab. A child mounts the first time its tab is selected and then
# stays mounted, hidden, so the Plotly figure keeps its state across switches.

# %%
tabs = ax.TabPanel(
    {
        "summary": ax.Text("Select the price tab to mount the figure."),
        "prices": price_figure(1, "ES prices"),
        "notes": ax.TextArea(value="Tab notes", label="Notes", rows=3),
    },
    titles={"summary": "Summary", "prices": "Prices", "notes": "Notes"},
    size="sm",
)
tabs

# %%
tabs.select_key("prices")
tabs.selected_key

# %%
tabs.add_tab(ax.Text("Added from Python"), "Added", key="added", select=True)
tabs.titles

# %% [markdown]
# ## StackedPanel
#
# Shows one child at a time without a tab strip. Drive it from a selector or
# from Python.

# %%
stacked = ax.StackedPanel(
    {"table": ax.Text("Table view"), "chart": price_figure(2, "NQ prices")},
)
view = ax.SegmentedControl(["table", "chart"], value="table", label="View")
view.observe(lambda change: stacked.select_key(change["new"]), names="value")
ax.Stack({"view": view, "panel": stacked}, gap=2)

# %%
view.value = "chart"
stacked.selected_key

# %% [markdown]
# ## AccordionPanel
#
# Titled collapsible sections. `value` holds the open section key, or a list of
# keys with `multiple=True`.

# %%
accordion = ax.AccordionPanel(
    {
        "market": ax.Stack(
            {
                "s0": ax.Slider(6000, label="Spot", min=5400, max=6600, step=1),
                "vol": ax.Slider(15, label="Vol (%)", min=5, max=50, step=0.5),
            },
            gap=1,
        ),
        "rates": ax.NumberInput(5.0, label="Rate (%)", step=0.25),
        "notes": ax.Text("Accordion sections keep their widgets mounted."),
    },
    titles={"market": "Market", "rates": "Rates", "notes": "Notes"},
)
accordion

# %%
accordion.open_key("rates")
accordion.open_keys

# %% [markdown]
# ## ScrollBox
#
# A fixed-height scrolling region for long control lists or logs.

# %%
scroll = ax.ScrollBox(
    [ax.Text(f"Fill {index + 1}: 10 @ {100 + index * 0.25:.2f}") for index in range(40)],
    label="Fills",
    height=160,
)
scroll

# %% [markdown]
# ## SplitPanel
#
# Draggable panes. Drags write fractions back to `sizes`, and assigning `sizes`
# from Python resizes the panes.

# %%
split = ax.SplitPanel(
    {
        "controls": ax.Stack(
            {
                "symbol": ax.TextInput("ES", label="Symbol", size="sm"),
                "quantity": ax.NumberInput(1, label="Quantity", size="sm"),
                "status": status,
            },
            gap=2,
        ),
        "chart": price_figure(3, "Split chart"),
    },
    sizes=[0.3, 0.7],
    height=320,
)
split

# %%
split.sizes = [0.5, 0.5]
split.sizes

# %% [markdown]
# ## ResponsivePanel
#
# A stack that lays children out side by side when the output is wider than the
# breakpoint and stacks them below it. Narrow the browser window to see it
# switch.

# %%
responsive = ax.ResponsivePanel(
    {
        "left": price_figure(4, "Left"),
        "right": price_figure(5, "Right"),
    },
    breakpoint=900,
)
responsive

# %% [markdown]
# ## Composition
#
# Panels nest like any other anylumino widget, so a tab panel can hold a split
# panel that holds an accordion.

# %%
workspace = ax.TabPanel(
    {
        "desk": ax.SplitPanel(
            {
                "controls": ax.AccordionPanel(
                    {
                        "market": ax.Slider(6000, label="Spot", min=5400, max=6600, step=1),
                        "rates": ax.NumberInput(5.0, label="Rate (%)", step=0.25),
                    },
                    titles={"market": "Market", "rates": "Rates"},
                ),
                "chart": price_figure(6, "Desk chart"),
            },
            sizes=[0.35, 0.65],
            height=300,
        ),
        "log": ax.ScrollBox([ax.Text(f"Event {index + 1}") for index in range(25)], label="Events", height=200),
    },
    titles={"desk": "Desk", "log": "Log"},
    size="sm",
)
workspace
