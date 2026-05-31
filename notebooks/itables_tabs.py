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
# # anylumino with itables
#
# `itables.widget.ITable` is an AnyWidget, so it can be placed directly inside
# an `anylumino.TabPanel`. This example appends rows to a pandas DataFrame and
# calls `ITable.update(...)` so the table inside the tab reflects the new data.

# %%
from __future__ import annotations

import pandas as pd
from itables.widget import ITable

from anylumino import Button
from anylumino import Dropdown
from anylumino import IntSlider
from anylumino import SplitPanel
from anylumino import TabPanel
from anylumino import TextInput
from anylumino import TextWidget
from anylumino import Toolbar
from anylumino import VBox


# %%
def initial_trades() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"trade_id": 1, "symbol": "AAPL", "side": "BUY", "quantity": 100, "price": 189.24},
            {"trade_id": 2, "symbol": "MSFT", "side": "SELL", "quantity": 75, "price": 421.16},
            {"trade_id": 3, "symbol": "NVDA", "side": "BUY", "quantity": 40, "price": 908.88},
        ],
    )


def total_notional(df: pd.DataFrame) -> float:
    return float((df["quantity"] * df["price"]).sum())


def make_summary(df: pd.DataFrame) -> str:
    return (
        f"Rows: {len(df)}\n"
        f"Total quantity: {int(df['quantity'].sum())}\n"
        f"Total notional: {total_notional(df):,.2f}"
    )


# %%
state = {
    "df": initial_trades(),
    "next_trade_id": 4,
}

symbol_input = TextInput(value="AAPL", description="Symbol")
side_input = Dropdown(options=["BUY", "SELL"], value="BUY", description="Side")
quantity_input = IntSlider(value=50, min=1, max=500, step=1, description="Quantity")
price_input = IntSlider(value=190, min=1, max=1000, step=1, description="Price")
add_button = Button(description="Add row", button_style="primary", icon="plus")
reset_button = Button(description="Reset", icon="rotate-left")
status = TextWidget("Ready. Press Add row to append to the DataFrame and refresh the ITable.")
summary = TextWidget(make_summary(state["df"]))

table = ITable(
    state["df"],
    caption="Trades",
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
        caption=f"Trades ({len(state['df'])} rows)",
        selected_rows=selected_rows,
    )
    summary.text = make_summary(state["df"])


def append_trade(_event: object | None = None) -> None:
    trade_id = int(state["next_trade_id"])
    row = {
        "trade_id": trade_id,
        "symbol": symbol_input.value.upper(),
        "side": side_input.value,
        "quantity": int(quantity_input.value),
        "price": float(price_input.value),
    }
    state["df"] = pd.concat([state["df"], pd.DataFrame([row])], ignore_index=True)
    state["next_trade_id"] = trade_id + 1
    refresh_table(selected_row=len(state["df"]) - 1)
    status.text = f"Added trade {trade_id} to the DataFrame and refreshed the table."


def reset_trades(_event: object | None = None) -> None:
    state["df"] = initial_trades()
    state["next_trade_id"] = 4
    refresh_table(selected_row=len(state["df"]) - 1)
    status.text = "Reset the DataFrame and refreshed the table."


add_button.on_click(append_trade)
reset_button.on_click(reset_trades)


# %%
toolbar = Toolbar(
    [
        {"id": "add", "label": "Add row", "icon": "plus"},
        {"id": "reset", "label": "Reset", "icon": "rotate-left"},
    ],
    callbacks={
        "add": lambda _id: append_trade(),
        "reset": lambda _id: reset_trades(),
    },
)

controls = VBox(
    {
        "symbol": symbol_input,
        "side": side_input,
        "quantity": quantity_input,
        "price": price_input,
        "add": add_button,
        "reset": reset_button,
        "status": status,
    },
    height=340,
    scroll=True,
)

tabs = TabPanel(
    {
        "trades": table,
        "summary": summary,
    },
    titles={"trades": "Live table", "summary": "Summary"},
    height=460,
)

dashboard = SplitPanel(
    {
        "controls": controls,
        "table": VBox({"toolbar": toolbar, "tabs": tabs}, height=500),
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
