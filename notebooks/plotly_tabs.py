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
# # anylumino Plotly tab smoke test
#
# This notebook exercises `anylumino.TabPanel` with basic anywidget children
# and Plotly `FigureWidget` children.

# %%
from __future__ import annotations

import math

import plotly.graph_objects as go

from anylumino import TabPanel
from anylumino import TextWidget


def make_wave_figure(title: str, phase: float = 0.0) -> go.FigureWidget:
    x_values = list(range(80))
    y_values = [math.sin(index / 8 + phase) + 0.2 * math.cos(index / 3) for index in x_values]
    figure = go.FigureWidget()
    figure.add_scatter(x=x_values, y=y_values, mode="lines", name=title)
    figure.update_layout(
        title=title,
        height=420,
        margin={"l": 42, "r": 24, "t": 54, "b": 42},
        template="plotly_white",
    )
    return figure


# %% [markdown]
# ## Basic anywidget children

# %%
TabPanel(
    {
        "first": TextWidget("This is an anywidget child rendered in a Lumino tab."),
        "second": TextWidget("The second tab is a separate child widget."),
    },
    titles={"first": "First", "second": "Second"},
    width="100%",
    height=260,
)

# %% [markdown]
# ## Plotly children

# %%
daily_signal = make_wave_figure("Daily sensor signal")
weekly_signal = make_wave_figure("Weekly comparison", phase=0.9)

plot_tabs = TabPanel(
    {"daily": daily_signal},
    titles={"daily": "Daily signal"},
    selected_index=0,
    width="100%",
    height=520,
)

plot_tabs

# %% [markdown]
# ## Add a Plotly tab after display

# %%
plot_tabs.add_tab(weekly_signal, "Weekly comparison", key="weekly", select=True)

# %%
