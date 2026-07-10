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
# # anylumino Astryx table

# %%
from __future__ import annotations

from anylumino.astryx import Badge
from anylumino.astryx import Card
from anylumino.astryx import Divider
from anylumino.astryx import Heading
from anylumino.astryx import Stack
from anylumino.astryx import Table


table = Table(
    rows=[
        {
            "symbol": "AAPL",
            "price": 195.12,
            "venue": "XNAS",
            "status": "Open",
            "qty": 400,
        },
        {
            "symbol": "MSFT",
            "price": 423.85,
            "venue": "XNAS",
            "status": "Open",
            "qty": 250,
        },
        {
            "symbol": "NVDA",
            "price": 141.36,
            "venue": "XNAS",
            "status": "Closed",
            "qty": 900,
        },
        {
            "symbol": "ASML",
            "price": 931.44,
            "venue": "XAMS",
            "status": "Open",
            "qty": 80,
        },
    ],
    columns=[
        {
            "key": "symbol",
            "header": "Symbol",
            "sortable": True,
            "width": {"kind": "proportional", "value": 1},
        },
        {
            "key": "price",
            "header": "Price",
            "sortable": True,
            "align": "end",
            "width": {"kind": "pixel", "value": 96},
        },
        {
            "key": "qty",
            "header": "Qty",
            "sortable": True,
            "align": "end",
            "width": {"kind": "pixel", "value": 72},
        },
        {
            "key": "venue",
            "header": "Venue",
            "sortable": True,
            "width": {"kind": "pixel", "value": 88},
        },
        {
            "key": "status",
            "header": "Status",
            "sortable": True,
            "width": {"kind": "proportional", "value": 1},
        },
    ],
    row_key="symbol",
    selected=["AAPL"],
    selects="multiple",
    sortable=True,
    sort_key="price",
    sort_direction="desc",
    density="compact",
    dividers="grid",
    hover=True,
    text_overflow="truncate",
    width="100%",
)

panel = Card(
    {
        "content": Stack(
            {
                "title": Stack(
                    {
                        "heading": Heading("Orders", level=3),
                        "badge": Badge("Live", variant="success"),
                    },
                    direction="horizontal",
                    align="center",
                    justify="between",
                    gap=3,
                    width="100%",
                ),
                "divider": Divider(),
                "table": table,
            },
            direction="vertical",
            gap=3,
            width="100%",
        ),
    },
    width="100%",
    padding=4,
)
panel

# %%
table.append_row(
    {"symbol": "TSLA", "price": 187.42, "venue": "XNAS", "status": "Open", "qty": 120}
)

# %%
table.prepend_row(
    {"symbol": "AMD", "price": 159.55, "venue": "XNAS", "status": "Open", "qty": 600}
)

# %%
table.update_row("MSFT", {"price": 426.11, "status": "Filled"})

# %%
table.remove_row("NVDA")

# %%
assert table.row_key == "symbol"
assert [row["symbol"] for row in table.rows] == ["AMD", "AAPL", "MSFT", "ASML", "TSLA"]
assert table.rows[2]["price"] == 426.11
assert table.rows[2]["status"] == "Filled"
assert table.selected == ["AAPL"]
assert table.selects == "multiple"
assert table.sort_key == "price"
assert table.sort_direction == "desc"
assert table.columns[1]["width"] == {"kind": "pixel", "value": 96}

# %%
