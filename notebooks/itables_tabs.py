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
# # anylumino with itables
#
# `itables.widget.ITable` is an AnyWidget, so it can be placed directly inside
# an `anylumino.TabPanel`. This example appends lab sample rows to a pandas
# DataFrame and calls `ITable.update(...)` so the table inside the tab reflects
# the new data.

# %%
from __future__ import annotations

import anylumino.astryx as ax
import pandas as pd
from itables.widget import ITable

from anylumino import SplitPanel
from anylumino import TabPanel
from anylumino import Toolbar
from anylumino import VBox


# %%
def initial_samples() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"sample_id": 1, "site": "North bed", "species": "Iris", "count": 12, "height_cm": 34.2},
            {"sample_id": 2, "site": "South bed", "species": "Daisy", "count": 18, "height_cm": 21.7},
            {"sample_id": 3, "site": "West bed", "species": "Lupine", "count": 9, "height_cm": 45.1},
        ],
    )


def mean_height(df: pd.DataFrame) -> float:
    return float(df["height_cm"].mean())


def make_summary(df: pd.DataFrame) -> str:
    return (
        f"- Rows: {len(df)}\n"
        f"- Total count: {int(df['count'].sum())}\n"
        f"- Mean height: {mean_height(df):.1f} cm"
    )


# %%
state = {
    "df": initial_samples(),
    "next_sample_id": 4,
}

site_input = ax.TextInput(value="East bed", label="Site")
species_input = ax.Selector(["Iris", "Daisy", "Lupine"], value="Iris", label="Species")
count_input = ax.Slider(10, min=1, max=50, step=1, label="Count", value_display="text")
height_input = ax.Slider(30, min=5, max=80, step=1, label="Height cm", value_display="text")
add_button = ax.Button("Add row", variant="primary")
reset_button = ax.Button("Reset")
status = ax.Text("Ready. Press Add row to append to the DataFrame and refresh the ITable.")
summary = ax.Markdown(make_summary(state["df"]))

table = ITable(
    state["df"],
    caption="Plant samples",
    select=True,
    selected_rows=[len(state["df"]) - 1],
    classes="display compact",
    pageLength=5,
)


# %%
def refresh_table(selected_row: int | None = None) -> None:
    selected_rows = [] if selected_row is None else [selected_row]
    table.update(
        state["df"],
        caption=f"Plant samples ({len(state['df'])} rows)",
        selected_rows=selected_rows,
    )
    summary.text = make_summary(state["df"])


def append_sample(_event: object | None = None) -> None:
    sample_id = int(state["next_sample_id"])
    row = {
        "sample_id": sample_id,
        "site": site_input.value,
        "species": species_input.value,
        "count": int(count_input.value),
        "height_cm": float(height_input.value),
    }
    state["df"] = pd.concat([state["df"], pd.DataFrame([row])], ignore_index=True)
    state["next_sample_id"] = sample_id + 1
    refresh_table(selected_row=len(state["df"]) - 1)
    status.text = f"Added sample {sample_id} to the DataFrame and refreshed the table."


def reset_samples(_event: object | None = None) -> None:
    state["df"] = initial_samples()
    state["next_sample_id"] = 4
    refresh_table(selected_row=len(state["df"]) - 1)
    status.text = "Reset the DataFrame and refreshed the table."


add_button.on_click(append_sample)
reset_button.on_click(reset_samples)


# %%
toolbar = Toolbar(
    [
        {"id": "add", "label": "Add row", "icon": "AddContent"},
        {"id": "reset", "label": "Reset", "icon": "RotateRight"},
    ],
    callbacks={
        "add": lambda _id: append_sample(),
        "reset": lambda _id: reset_samples(),
    },
)

controls = VBox(
    {
        "site": site_input,
        "species": species_input,
        "count": count_input,
        "height": height_input,
        "add": add_button,
        "reset": reset_button,
        "status": status,
    },
    height=340,
    scroll=True,
)

tabs = TabPanel(
    {
        "samples": table,
        "summary": summary,
    },
    titles={"samples": "Live table", "summary": "Summary"},
    height=460,
)

dashboard = SplitPanel(
    {
        "controls": controls,
        "table": VBox(
            {"toolbar": toolbar, "tabs": tabs},
            stretches=[0, 1],
            child_min_height=36,
            height=500,
        ),
    },
    sizes=[0.28, 0.72],
    height=540,
)

dashboard

# %% [markdown]
# ## What matters
#
# The `ITable` instance is the child of the `TabPanel`. The callback keeps the
# source data in `state["df"]`, appends a row, then calls:
#
# ```python
# table.update(state["df"], selected_rows=[len(state["df"]) - 1])
# ```
#
# That is the part that pushes the updated DataFrame to the already-displayed
# table widget inside the anylumino tab.

# %%
