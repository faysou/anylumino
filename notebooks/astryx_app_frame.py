# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Astryx app frame

# %% [markdown]
# An `AppShell` with top and side navigation around a `Layout`, plus the step,
# overflow, selector, rich text, timer, indicator, and toast widgets.

# %%
from __future__ import annotations

from datetime import datetime
from datetime import timedelta

import anylumino.astryx as ax

toast = ax.Toast(position="bottomEnd")
status = ax.Text("Select a page", text_type="supporting", color="secondary")

top = ax.TopNav(
    ["Orders", "Fills", {"label": "Reports", "items": [{"label": "Daily P&L", "value": "pnl"}, "Exposure"]}],
    "Orders",
    heading="Trading desk",
    icon="menu",
    end=[ax.Button("Help", variant="ghost"), toast],
)
side = ax.SideNav(
    [
        {"label": "Overview", "value": "overview", "icon": "info"},
        {"type": "section", "title": "Desk", "items": [{"label": "Orders", "value": "orders", "icon": "check"}, "Fills"]},
    ],
    "overview",
    heading="Paper account",
    subheading="DU1234567",
    collapsible=True,
)
steps = ax.Stepper(["Draft", "Review", "Send"], 1, label="Order ticket", navigable=True)
actions = ax.OverflowList(
    ["Refresh", "Export CSV", "Cancel all", "Flatten", "Settings"],
    max_visible=3,
    action_callbacks=[lambda _widget, action: toast.notify(f"Ran {action}")],
)
symbol = ax.ComplexSelector(
    ax.VStack(
        [
            ax.Button("AAPL", callbacks=[lambda _button: (setattr(symbol, "value", "AAPL"), symbol.hide())]),
            ax.Button("MSFT", callbacks=[lambda _button: (setattr(symbol, "value", "MSFT"), symbol.hide())]),
        ],
        gap=1,
        padding=2,
    ),
    "AAPL",
    label="Symbol",
)
notes = ax.RichTextEditor("## Plan\n\n- Buy **AAPL** on the open", label="Notes", continuous_update=False)
preview = ax.RichTextView("## Plan\n\n- Buy **AAPL** on the open")
notes.observe(lambda change: setattr(preview, "text", change["new"]), names="value")
session = ax.HStack(
    [
        ax.Timer(datetime.now() - timedelta(minutes=12), format="clock"),
        ax.Indicator("checked", kind="check"),
        ax.Indicator("indeterminate"),
        ax.Indicator("checked", kind="radio"),
        ax.NavIcon("menu"),
    ],
    gap=3,
    align="center",
)

layout = ax.Layout(
    ax.VStack([steps, actions, symbol, notes, preview], gap=3),
    header=ax.Heading("Orders", level=3),
    end=session,
    footer=status,
    end_width=220,
    dividers=True,
)
shell = ax.AppShell(layout, top_nav=top, side_nav=side, height="auto")
side.on_action(lambda _widget, page: setattr(status, "text", f"Page: {page}"))
top.on_action(lambda _widget, page: setattr(status, "text", f"Top: {page}"))

shell

# %%
toast.notify("Order filled: 100 AAPL")

# %%
toast.notify("Order rejected: insufficient margin", type="error")

# %%
steps.value = 2
notes.value = "## Plan\n\n- Sell **MSFT** at the close"

# %%
assert shell.child_keys == ["content", "top_nav", "side_nav"]
assert layout.child_keys == ["content", "header", "end", "footer"]
assert (steps.value, symbol.value) == (2, "AAPL")

# %%
