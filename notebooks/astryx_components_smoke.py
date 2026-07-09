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
# # Astryx components smoke test
#
# This notebook exercises Astryx-backed anylumino widgets in a JupyterLab-sized
# panel. The layout intentionally stays dense and quiet so it fits notebook use.

# %%
from __future__ import annotations

import anylumino as al


clicks = {"count": 0}
status = al.TextWidget("astryx status: ready")


def record_click(_button):
    clicks["count"] += 1
    status.value = f"astryx status: clicked {clicks['count']}"


title = al.AstryxText("Astryx component render check", props={"type": "large", "weight": "semibold"})
subtitle = al.AstryxText(
    "Notebook-safe Astryx controls, display widgets, generated lists, tables, and composed layouts.",
    props={"type": "supporting", "color": "secondary"},
)
breadcrumbs = al.AstryxBreadcrumbs(
    [
        {"label": "Notebook", "href": "#"},
        {"label": "Astryx", "href": "#"},
        {"label": "Components", "current": True},
    ],
    variant="supporting",
)
connected = al.AstryxStatusDot("Connected", variant="success", isPulsing=True)
badge = al.AstryxBadge("Live", variant="success")
progress = al.AstryxProgressBar(58, label="Render coverage", variant="success", hasValueLabel=True)
banner = al.AstryxBanner(
    "Astryx widgets loaded",
    status="success",
    description="All sections render inside one scrollable Jupyter output.",
)


header = al.AstryxSection(
    {
        "breadcrumbs": breadcrumbs,
        "title": title,
        "subtitle": subtitle,
        "state": al.AstryxStack(
            {
                "dot": connected,
                "badge": badge,
                "progress": progress,
            },
            direction="horizontal",
            gap=3,
            align="center",
            wrap="wrap",
        ),
        "banner": banner,
    },
    variant="transparent",
    padding=3,
)


symbol = al.AstryxTextInput(value="AAPL", label="Symbol", placeholder="Ticker", hasClear=True, width="220px")
notes = al.AstryxTextArea(value="Watch opening auction imbalance.", label="Notes", rows=3, width="320px")
limit = al.AstryxNumberInput(value=250, label="Order limit", min=0, max=1000, step=10, units="sh", width="180px")
risk = al.AstryxSlider(value=42, label="Risk budget", min=0, max=100, valueDisplay="text", width="260px")
dataset = al.AstryxSelector(
    [("Latency", "latency"), ("Volume", "volume"), ("Fills", "fills")],
    value="latency",
    label="Metric",
    width="220px",
)
fields = al.AstryxMultiSelector(
    ["Bid", "Ask", "Last", "Size", "Venue"],
    value=["Bid", "Ask", "Last"],
    label="Fields",
    triggerDisplay="badges",
    width="260px",
)
trade_date = al.AstryxDateInput(value="2026-07-09", label="Trade date", width="180px")
trade_time = al.AstryxTimeInput(value="14:30", label="Time", hourFormat="24h", width="160px")
enabled = al.AstryxCheckbox(value=True, label="Enabled")
stream = al.AstryxSwitch(value=False, label="Stream")
pinned = al.AstryxToggleButton(value=True, label="Pinned")
density = al.AstryxSegmentedControl(
    ["Compact", "Standard", "Detailed"],
    value="Standard",
    label="Density",
    size="sm",
)
mode = al.AstryxRadioList(["Auto", "Manual"], value="Auto", label="Mode", orientation="horizontal")
streams = al.AstryxCheckboxList(["Quotes", "Trades", "Depth"], value=["Quotes", "Trades"], label="Streams")


controls = al.AstryxGrid(
    {
        "symbol": symbol,
        "notes": notes,
        "limit": limit,
        "risk": risk,
        "dataset": dataset,
        "fields": fields,
        "date": trade_date,
        "time": trade_time,
        "toggles": al.AstryxStack(
            {"enabled": enabled, "stream": stream, "pinned": pinned},
            direction="horizontal",
            gap=3,
            align="center",
            wrap="wrap",
        ),
        "density": density,
        "mode": mode,
        "streams": streams,
    },
    columns={"minWidth": 220, "repeat": "fit"},
    gap=4,
    width="100%",
)

wrapped_symbol = al.AstryxField(
    al.AstryxTextInput(value="NVDA", label="Symbol", isLabelHidden=True, width="180px"),
    label="Wrapped symbol",
    description="Field wrapper around a custom input",
    width="220px",
)
grouped_qty = al.AstryxInputGroup(
    al.AstryxNumberInput(value=100, label="Quantity", isLabelHidden=True),
    label="Quantity",
    suffix="sh",
    width="220px",
)
calendar = al.AstryxCalendar("2026-07-09", hasWeekNumbers=True)
file_input = al.AstryxFileInput(label="Upload CSV", accept=".csv", mode="input", width="240px")
form_layout = al.AstryxFormLayout(
    {"field": wrapped_symbol, "quantity": grouped_qty, "file": file_input},
    direction="vertical",
)


rows = [
    {"id": "AAPL", "symbol": "AAPL", "side": "BUY", "status": "Live"},
    {"id": "MSFT", "symbol": "MSFT", "side": "SELL", "status": "Queued"},
    {"id": "NVDA", "symbol": "NVDA", "side": "BUY", "status": "Paused"},
]
orders = al.AstryxTable(
    rows,
    [
        {"key": "symbol", "header": "Symbol", "width": {"kind": "proportional", "value": 1}},
        {"key": "side", "header": "Side", "width": {"kind": "pixel", "value": 90}},
        {"key": "status", "header": "Status", "width": {"kind": "proportional", "value": 1}},
    ],
    density="compact",
    dividers="grid",
    hasHover=True,
)
watchlist = al.AstryxList(
    [
        {"label": "Opening imbalance", "description": "Auction monitor"},
        {"label": "Venue latency", "description": "P95 execution path"},
        {"label": "Risk checks", "description": "Pre-trade guardrails"},
    ],
    header="Watchlist",
    hasDividers=True,
    density="compact",
)
metadata = al.AstryxMetadataList(
    [
        {"label": "Account", "value": "SIM-001"},
        {"label": "Region", "value": "US equities"},
        {"label": "Updated", "value": "2026-07-09 14:30"},
    ],
    columns="multi",
)
tabs = al.AstryxTabList(["Summary", "Orders", "Risk"], value="Summary", layout="fill", hasDivider=True)
button_group = al.AstryxButtonGroup(
    [
        {"label": "Apply", "variant": "primary"},
        {"label": "Stage"},
        {"label": "Cancel", "variant": "ghost"},
    ],
    label="Order actions",
    callbacks=[record_click],
)
apply_button = al.AstryxButton("Apply", variant="primary", callbacks=[record_click])
more_button = al.AstryxIconButton("More actions", icon="moreHorizontal", variant="ghost", callbacks=[record_click])
dropdown = al.AstryxDropdownMenu(
    [
        {"label": "Refresh", "value": "refresh"},
        {"label": "Export", "value": "export"},
    ],
    label="Actions",
    callbacks=[record_click],
)
more_menu = al.AstryxMoreMenu(["Edit", "Duplicate", "Archive"], callbacks=[record_click])


data_section = al.AstryxGrid(
    {
        "orders": al.AstryxCard({"table": orders}, padding=2, width="100%"),
        "list": al.AstryxCard({"watchlist": watchlist}, padding=3),
        "metadata": al.AstryxCard({"metadata": metadata}, padding=3),
        "tabs": al.AstryxCard(
            {
                "tabs": tabs,
                "actions": al.AstryxStack(
                    {"group": button_group, "apply": apply_button, "menu": dropdown, "more_menu": more_menu, "more": more_button},
                    direction="horizontal",
                    gap=2,
                    align="center",
                    wrap="wrap",
                ),
            },
            padding=3,
        ),
    },
    columns={"minWidth": 300, "repeat": "fit"},
    gap=3,
    width="100%",
)


avatar = al.AstryxAvatar("Ada Lovelace", size="medium")
avatar_group = al.AstryxAvatarGroup(["Ada Lovelace", "Grace Hopper", "Katherine Johnson"], overflow_count=2, size="small")
icon = al.AstryxIcon("check", size="md", color="success")
token = al.AstryxToken("sim", color="blue")
kbd = al.AstryxKbd("mod+enter")
skeleton = al.AstryxSkeleton(width=160, height=16)
spinner = al.AstryxSpinner(size="sm", label="Loading")
empty = al.AstryxEmptyState("No rejected orders", description="Rejected order events will appear here.", isCompact=True)
code = al.AstryxCodeBlock("order = {'symbol': 'AAPL', 'side': 'BUY'}", language="python", hasLineNumbers=False)
inline_code = al.AstryxCode("order_id")
markdown = al.AstryxMarkdown("**Markdown** with `inline code` and a compact list:\n\n- quotes\n- trades", density="compact")
quote = al.AstryxBlockquote("Design system widgets can compose cleanly inside Jupyter outputs.")
timestamp = al.AstryxTimestamp("2026-07-09T14:30:00Z", format="system_date_time", isTimezoneShown=True)
thumbnail = al.AstryxThumbnail(label="preview.png", isLoading=True)
citation = al.AstryxCitation({"title": "Run report", "url": "#"}, number=1)
outline = al.AstryxOutline(
    [
        {"id": "summary", "label": "Summary", "level": 1},
        {"id": "orders", "label": "Orders", "level": 2},
        {"id": "risk", "label": "Risk", "level": 2},
    ],
    active_id="summary",
)
tree = al.AstryxTreeList(
    [
        {
            "id": "catalog",
            "label": "catalog",
            "description": "Market data",
            "isExpanded": True,
            "children": [
                {"id": "quotes", "label": "quotes.parquet"},
                {"id": "trades", "label": "trades.parquet"},
            ],
        },
    ],
    header="Artifacts",
    density="compact",
)
tooltip = al.AstryxTooltip("Runs validation", al.AstryxButton("Validate", variant="secondary"))
hover = al.AstryxHoverCard(al.AstryxText("Last run: success"), al.AstryxButton("Run state"))
popover = al.AstryxPopover(al.AstryxText("Compact popover content"), al.AstryxButton("Open"), label="Details")
details = al.AstryxCollapsible(al.AstryxMarkdown("Verbose diagnostics can live here."), trigger="Diagnostics", default_open=False)


visuals = al.AstryxGrid(
    {
        "identity": al.AstryxCard(
            {
                "row": al.AstryxStack(
                    {"avatar": avatar, "group": avatar_group, "icon": icon, "token": token, "kbd": kbd, "time": timestamp},
                    direction="horizontal",
                    gap=3,
                    align="center",
                    wrap="wrap",
                )
            },
            padding=3,
        ),
        "loading": al.AstryxCard(
            {
                "spinner": spinner,
                "skeleton": skeleton,
                "thumbnail": thumbnail,
            },
            padding=3,
        ),
        "empty": al.AstryxCard({"empty": empty}, padding=3),
        "content": al.AstryxCard(
            {
                "inline": al.AstryxStack(
                    {"code": inline_code, "citation": citation},
                    direction="horizontal",
                    gap=2,
                    align="center",
                ),
                "markdown": markdown,
                "divider": al.AstryxDivider(),
                "quote": quote,
                "code": code,
            },
            padding=3,
        ),
        "structure": al.AstryxCard(
            {
                "form": form_layout,
                "calendar": calendar,
                "outline": outline,
                "tree": tree,
                "overlays": al.AstryxStack(
                    {"tooltip": tooltip, "hover": hover, "popover": popover},
                    direction="horizontal",
                    gap=2,
                    wrap="wrap",
                ),
                "details": details,
            },
            padding=3,
        ),
    },
    columns={"minWidth": 300, "repeat": "fit"},
    gap=3,
    width="100%",
)


app = al.VBox(
    {
        "header": header,
        "controls": controls,
        "data": data_section,
        "visuals": visuals,
        "status": status,
    },
    width="100%",
    height=780,
    spacing=12,
    scroll=True,
    resizable=False,
)

app

# %%
assert symbol.value == "AAPL"
assert enabled.value is True
assert stream.value is False
assert pinned.value is True
assert density.value == "Standard"
assert dataset.value == "latency"
assert fields.value == ["Bid", "Ask", "Last"]
assert controls.component_name == "Grid"
assert controls.child_keys == [
    "symbol",
    "notes",
    "limit",
    "risk",
    "dataset",
    "fields",
    "date",
    "time",
    "toggles",
    "density",
    "mode",
    "streams",
]
assert orders.component_name == "Table"
assert tabs.props["items"] == ["Summary", "Orders", "Risk"]
assert button_group.props["items"][0]["label"] == "Apply"
assert form_layout.component_name == "FormLayout"
assert wrapped_symbol.component_name == "Field"
assert grouped_qty.component_name == "InputGroup"
assert calendar.component_name == "Calendar"
assert dropdown.component_name == "DropdownMenu"
assert more_menu.component_name == "MoreMenu"
assert outline.component_name == "Outline"
assert tree.component_name == "TreeList"
assert tooltip.child_keys == ["trigger"]
assert popover.child_keys == ["trigger", "content"]
