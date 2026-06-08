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
# # anylumino Spectrum table

# %%
from __future__ import annotations

from anylumino import Table


table = Table(
    rows=[
        {"symbol": "AAPL", "price": 195.12, "venue": "XNAS", "status": "Open"},
        {"symbol": "MSFT", "price": 423.85, "venue": "XNAS", "status": "Open"},
        {"symbol": "NVDA", "price": 141.36, "venue": "XNAS", "status": "Closed"},
        {"symbol": "ASML", "price": 931.44, "venue": "XAMS", "status": "Open"},
    ],
    columns=[
        {"key": "symbol", "label": "Symbol", "sortable": True},
        {"key": "price", "label": "Price", "align": "end", "sortable": True},
        {"key": "venue", "label": "Venue", "sortable": True},
        {"key": "status", "label": "Status"},
    ],
    row_key="symbol",
    selected=["AAPL"],
    selects="multiple",
    sortable=True,
    density="compact",
    quiet=True,
    width="720px",
)
table

# %%
table.append_row({"symbol": "TSLA", "price": 187.42, "venue": "XNAS", "status": "Open"})

# %%
table.prepend_row({"symbol": "AMD", "price": 159.55, "venue": "XNAS", "status": "Open"})

# %%
table.update_row("MSFT", {"price": 426.11, "status": "Filled"})

# %%
table.remove_row("NVDA")
