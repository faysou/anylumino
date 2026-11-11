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
# # anylumino Tabulator streaming

# %% [markdown]
# A blotter that takes price updates at 10 Hz inside a `TabPanel`. Each tick
# sends one `upsert_rows` call with every changed row, so the browser repaints
# once per tick. Batch rows per call: one message per row costs one message
# each.

# %%
from __future__ import annotations

import asyncio
import random

import anylumino as al


symbols = ["ESZ6", "NQZ6", "RTYZ6", "YMZ6", "CLZ6", "GCZ6", "SIZ6", "ZNZ6"]
prices = {"ESZ6": 5012.25, "NQZ6": 18011.5, "RTYZ6": 2310.1, "YMZ6": 43120.0, "CLZ6": 71.2, "GCZ6": 2650.4, "SIZ6": 31.05, "ZNZ6": 110.5}
blotter = al.Tabulator(
    [{"id": symbol, "symbol": symbol, "last": price, "change": 0.0, "ticks": 0} for symbol, price in prices.items()],
    [
        {"title": "Symbol", "field": "symbol"},
        {"title": "Last", "field": "last", "hozAlign": "right"},
        {
            "title": "Change",
            "field": "change",
            "hozAlign": "right",
            "formatter": al.JsCode(
                "function(cell) { const v = cell.getValue(); cell.getElement().style.color = v < 0 ? '#c62828' : '#2e7d32'; return v.toFixed(2); }"
            ),
        },
        {"title": "Ticks", "field": "ticks", "hozAlign": "right"},
    ],
    options={"layout": "fitColumns"},
)
tabs = al.TabPanel(
    [blotter, al.TextWidget("Notes go here.")],
    titles=["Blotter", "Notes"],
    height=320,
)
tabs

# %%
ticks = {symbol: 0 for symbol in symbols}


async def stream(
    seconds: float = 5.0,
    rate: float = 10.0,
) -> int:
    count = 0
    for _ in range(int(seconds * rate)):
        changed = random.sample(
            symbols,
            3,
        )
        updates = []
        for symbol in changed:
            move = random.gauss(
                0,
                prices[symbol] * 0.0005,
            )
            change = round(
                move,
                2,
            )
            prices[symbol] = round(
                prices[symbol] + change,
                2,
            )
            ticks[symbol] += 1
            updates.append({"id": symbol, "last": prices[symbol], "change": change, "ticks": ticks[symbol]})

        blotter.upsert_rows(updates)
        count += 1
        await asyncio.sleep(1 / rate)

    return count


await stream()
blotter.revision
