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
# # anylumino Tabulator grid

# %% [markdown]
# `al.Tabulator` is a virtualized data grid built on Tabulator 6.7. Its
# `columns` and `options` take Tabulator's own names, so the
# [Tabulator documentation](https://tabulator.info/docs/6.7) applies. Python
# holds the rows: row methods send only the changed rows to the browser.

# %%
from __future__ import annotations

from datetime import datetime

import anylumino as al


rows = [
    {"id": 1, "symbol": "ESZ6", "side": "buy", "last": 5012.25, "qty": 3, "filled": "2026-11-11T09:30"},
    {"id": 2, "symbol": "NQZ6", "side": "sell", "last": 18011.5, "qty": -1, "filled": "2026-11-11T09:42"},
    {"id": 3, "symbol": "RTYZ6", "side": "buy", "last": 2310.1, "qty": 10, "filled": "2026-11-10T15:05"},
]
for row in rows:
    row["filled"] = datetime.fromisoformat(row["filled"])

# %% [markdown]
# ## Columns, editors, and JavaScript functions

# %% [markdown]
# `al.JsCode` passes a JavaScript function wherever Tabulator takes one. The
# `datetime` formatter and sorter work by name, because the widget bundles
# luxon. Select a row, edit `Side` or `Qty`, or open the `Symbol` header menu.

# %%
columns = [
    {
        "title": "Symbol",
        "field": "symbol",
        "headerMenu": [
            {
                "label": "Hide column",
                "action": al.JsCode("(event, column) => column.hide()"),
            }
        ],
    },
    {
        "title": "Side",
        "field": "side",
        "editor": "list",
        "editorParams": {"values": ["buy", "sell"]},
    },
    {
        "title": "Last",
        "field": "last",
        "hozAlign": "right",
        "formatter": al.JsCode("function(cell) { return cell.getValue().toFixed(2); }"),
    },
    {
        "title": "Qty",
        "field": "qty",
        "hozAlign": "right",
        "editor": "number",
    },
    {
        "title": "Filled",
        "field": "filled",
        "formatter": "datetime",
        "formatterParams": {"inputFormat": "iso", "outputFormat": "dd/MM HH:mm"},
        "sorter": "datetime",
        "sorterParams": {"format": "iso"},
    },
]
table = al.Tabulator(
    rows,
    columns,
    options={"layout": "fitColumns", "selectableRows": True},
    height=220,
)
table

# %% [markdown]
# ## Events

# %% [markdown]
# `selected` holds the index values of the selected rows. `on_edit` receives a
# `CellEdit` for every edit made in the grid.

# %%
edits = []


def record_edit(
    widget: al.Tabulator,
    edit: al.CellEdit,
) -> None:
    edits.append(edit)


table.on_edit(record_edit)
table.selected = [2]
table.selected

# %% [markdown]
# ## Row changes from Python

# %%
table.update_rows([{"id": 1, "last": 5013.0}])
table.add_rows(
    [
        {
            "id": 4,
            "symbol": "CLZ6",
            "side": "buy",
            "last": 71.2,
            "qty": 2,
            "filled": datetime.fromisoformat("2026-11-11T10:01"),
        }
    ]
)
table.delete_rows([3])
[row["symbol"] for row in table.data]

# %% [markdown]
# ## DataFrames

# %% [markdown]
# A DataFrame travels as Arrow IPC when `pyarrow` is installed. Without
# `columns`, the grid shows one column per field.

# %%
import pandas as pd


frame = pd.DataFrame(
    {
        "region": ["EMEA", "APAC", "AMER"],
        "revenue": [1.5, 2.0, 3.2],
    }
)
al.Tabulator(
    frame,
    height=160,
)
