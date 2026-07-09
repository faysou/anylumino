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
import anylumino.astryx as ax


brand = ax.Brand(
    "trading-desk",
    **{
        "color-accent": ("#0057b8", "#79b8ff"),
        "color-background-card": ("#ffffff", "#111827"),
        "color-text-primary": ("#111827", "#f9fafb"),
        "radius-container": "8px",
    },
)
clicks = {"count": 0}
status = al.TextWidget("astryx status: ready")


def record_click(_button):
    clicks["count"] += 1
    status.value = f"astryx status: clicked {clicks['count']}"


title = ax.Text("Astryx component render check", props={"type": "large", "weight": "semibold"})
subtitle = ax.Text(
    "Notebook-safe Astryx controls, display widgets, generated lists, tables, and composed layouts.",
    props={"type": "supporting", "color": "secondary"},
)
breadcrumbs = ax.Breadcrumbs(
    [
        {"label": "Notebook", "href": "#"},
        {"label": "Astryx", "href": "#"},
        {"label": "Components", "current": True},
    ],
    variant="supporting",
)
connected = ax.StatusDot("Connected", variant="success", isPulsing=True)
badge = ax.Badge("Live", variant="success")
progress = ax.ProgressBar(58, label="Render coverage", variant="success", hasValueLabel=True)
banner = ax.Banner(
    "Astryx widgets loaded",
    status="success",
    description="All sections render inside one scrollable Jupyter output.",
)


header = ax.Section(
    {
        "breadcrumbs": breadcrumbs,
        "title": title,
        "subtitle": subtitle,
        "state": ax.Stack(
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


symbol = ax.TextInput(value="AAPL", label="Symbol", placeholder="Ticker", hasClear=True, width="220px")
notes = ax.TextArea(value="Watch opening auction imbalance.", label="Notes", rows=3, width="320px")
limit = ax.NumberInput(value=250, label="Order limit", min=0, max=1000, step=10, units="sh", width="180px")
risk = ax.Slider(value=42, label="Risk budget", min=0, max=100, valueDisplay="text", width="260px")
dataset = ax.Selector(
    [("Latency", "latency"), ("Volume", "volume"), ("Fills", "fills")],
    value="latency",
    label="Metric",
    width="220px",
)
fields = ax.MultiSelector(
    ["Bid", "Ask", "Last", "Size", "Venue"],
    value=["Bid", "Ask", "Last"],
    label="Fields",
    triggerDisplay="badges",
    width="260px",
)
symbol_search = ax.Typeahead(
    [
        {"id": "AAPL", "label": "AAPL"},
        {"id": "MSFT", "label": "MSFT"},
        {"id": "NVDA", "label": "NVDA"},
    ],
    value="AAPL",
    label="Symbol search",
    width="220px",
)
field_tokens = ax.Tokenizer(["Bid", "Ask", "Last", "Size", "Venue"], value=["Bid", "Ask"], label="Tokenized fields", width="280px")
trade_date = ax.DateInput(value="2026-07-09", label="Trade date", width="180px")
trade_time = ax.TimeInput(value="14:30", label="Time", hourFormat="24h", width="160px")
enabled = ax.Checkbox(value=True, label="Enabled")
stream = ax.Switch(value=False, label="Stream")
pinned = ax.ToggleButton(value=True, label="Pinned")
density = ax.SegmentedControl(
    ["Compact", "Standard", "Detailed"],
    value="Standard",
    label="Density",
    size="sm",
)
mode = ax.RadioList(["Auto", "Manual"], value="Auto", label="Mode", orientation="horizontal")
streams = ax.CheckboxList(["Quotes", "Trades", "Depth"], value=["Quotes", "Trades"], label="Streams")


controls = ax.Grid(
    {
        "symbol": symbol,
        "notes": notes,
        "limit": limit,
        "risk": risk,
        "dataset": dataset,
        "fields": fields,
        "symbol_search": symbol_search,
        "field_tokens": field_tokens,
        "date": trade_date,
        "time": trade_time,
        "toggles": ax.Stack(
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

wrapped_symbol = ax.Field(
    ax.TextInput(value="NVDA", label="Symbol", isLabelHidden=True, width="180px"),
    label="Wrapped symbol",
    description="Field wrapper around a custom input",
    width="220px",
)
grouped_qty = ax.InputGroup(
    ax.NumberInput(value=100, label="Quantity", isLabelHidden=True),
    label="Quantity",
    suffix="sh",
    width="220px",
)
calendar = ax.Calendar("2026-07-09", hasWeekNumbers=True)
file_input = ax.FileInput(label="Upload CSV", accept=".csv", mode="input", width="240px")
form_layout = ax.FormLayout(
    {"field": wrapped_symbol, "quantity": grouped_qty, "file": file_input},
    direction="vertical",
)


rows = [
    {"id": "AAPL", "symbol": "AAPL", "side": "BUY", "status": "Live"},
    {"id": "MSFT", "symbol": "MSFT", "side": "SELL", "status": "Queued"},
    {"id": "NVDA", "symbol": "NVDA", "side": "BUY", "status": "Paused"},
]
orders = ax.Table(
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
watchlist = ax.List(
    [
        {"label": "Opening imbalance", "description": "Auction monitor"},
        {"label": "Venue latency", "description": "P95 execution path"},
        {"label": "Risk checks", "description": "Pre-trade guardrails"},
    ],
    header="Watchlist",
    hasDividers=True,
    density="compact",
)
metadata = ax.MetadataList(
    [
        {"label": "Account", "value": "SIM-001"},
        {"label": "Region", "value": "US equities"},
        {"label": "Updated", "value": "2026-07-09 14:30"},
    ],
    columns="multi",
)
tabs = ax.TabList(["Summary", "Orders", "Risk"], value="Summary", layout="fill", hasDivider=True)
button_group = ax.ButtonGroup(
    [
        {"label": "Apply", "variant": "primary"},
        {"label": "Stage"},
        {"label": "Cancel", "variant": "ghost"},
    ],
    label="Order actions",
    callbacks=[record_click],
)
apply_button = ax.Button("Apply", variant="primary", callbacks=[record_click])
more_button = ax.IconButton("More actions", icon="moreHorizontal", variant="ghost", callbacks=[record_click])
dropdown = ax.DropdownMenu(
    [
        {"label": "Refresh", "value": "refresh"},
        {"label": "Export", "value": "export"},
    ],
    label="Actions",
    callbacks=[record_click],
)
more_menu = ax.MoreMenu(["Edit", "Duplicate", "Archive"], callbacks=[record_click])


data_section = ax.Grid(
    {
        "orders": ax.Card({"table": orders}, padding=2, width="100%"),
        "list": ax.Card({"watchlist": watchlist}, padding=3),
        "metadata": ax.Card({"metadata": metadata}, padding=3),
        "tabs": ax.Card(
            {
                "tabs": tabs,
                "actions": ax.Stack(
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


avatar = ax.Avatar("Ada Lovelace", size="medium")
avatar_group = ax.AvatarGroup(["Ada Lovelace", "Grace Hopper", "Katherine Johnson"], overflow_count=2, size="small")
icon = ax.Icon("check", size="md", color="success")
token = ax.Token("sim", color="blue")
kbd = ax.Kbd("mod+enter")
skeleton = ax.Skeleton(width=160, height=16)
spinner = ax.Spinner(size="sm", label="Loading")
empty = ax.EmptyState("No rejected orders", description="Rejected order events will appear here.", isCompact=True)
code = ax.CodeBlock("order = {'symbol': 'AAPL', 'side': 'BUY'}", language="python", hasLineNumbers=False)
inline_code = ax.Code("order_id")
markdown = ax.Markdown("**Markdown** with `inline code` and a compact list:\n\n- quotes\n- trades", density="compact")
quote = ax.Blockquote("Design system widgets can compose cleanly inside Jupyter outputs.")
timestamp = ax.Timestamp("2026-07-09T14:30:00Z", format="system_date_time", isTimezoneShown=True)
thumbnail = ax.Thumbnail(label="preview.png", isLoading=True)
citation = ax.Citation({"title": "Run report", "url": "#"}, number=1)
outline = ax.Outline(
    [
        {"id": "summary", "label": "Summary", "level": 1},
        {"id": "orders", "label": "Orders", "level": 2},
        {"id": "risk", "label": "Risk", "level": 2},
    ],
    active_id="summary",
)
tree = ax.TreeList(
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
tooltip = ax.Tooltip("Runs validation", ax.Button("Validate", variant="secondary"))
hover = ax.HoverCard(ax.Text("Last run: success"), ax.Button("Run state"))
popover = ax.Popover(ax.Text("Compact popover content"), ax.Button("Open"), label="Details")
details = ax.Collapsible(ax.Markdown("Verbose diagnostics can live here."), trigger="Diagnostics", default_open=False)
palette = ax.CommandPalette(
    [
        {"id": "refresh", "label": "Refresh", "auxiliaryData": {"group": "Data"}},
        {"id": "export", "label": "Export CSV", "auxiliaryData": {"group": "Files"}},
    ],
    value="refresh",
    width=420,
)
dialog = ax.Dialog(ax.Text("Inline dialog content stays inside the notebook output."), open=True, width=360)
alert_dialog = ax.AlertDialog("Confirm action", "This inline preview uses the alert dialog surface.", action_label="Confirm")


visuals = ax.Grid(
    {
        "identity": ax.Card(
            {
                "row": ax.Stack(
                    {"avatar": avatar, "group": avatar_group, "icon": icon, "token": token, "kbd": kbd, "time": timestamp},
                    direction="horizontal",
                    gap=3,
                    align="center",
                    wrap="wrap",
                )
            },
            padding=3,
        ),
        "loading": ax.Card(
            {
                "spinner": spinner,
                "skeleton": skeleton,
                "thumbnail": thumbnail,
            },
            padding=3,
        ),
        "empty": ax.Card({"empty": empty}, padding=3),
        "content": ax.Card(
            {
                "inline": ax.Stack(
                    {"code": inline_code, "citation": citation},
                    direction="horizontal",
                    gap=2,
                    align="center",
                ),
                "markdown": markdown,
                "divider": ax.Divider(),
                "quote": quote,
                "code": code,
            },
            padding=3,
        ),
        "structure": ax.Card(
            {
                "form": form_layout,
                "calendar": calendar,
                "outline": outline,
                "tree": tree,
                "overlays": ax.Stack(
                    {"tooltip": tooltip, "hover": hover, "popover": popover},
                    direction="horizontal",
                    gap=2,
                    wrap="wrap",
                ),
                "details": details,
                "palette": palette,
                "dialog": dialog,
                "alert": alert_dialog,
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
        "theme": ax.Theme(
            {
                "header": header,
                "controls": controls,
                "data": data_section,
                "visuals": visuals,
            },
            brand=brand,
            gap=3,
        ),
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
assert symbol_search.value == "AAPL"
assert field_tokens.value == ["Bid", "Ask"]
assert controls.component_name == "Grid"
assert controls.child_keys == [
    "symbol",
    "notes",
    "limit",
    "risk",
    "dataset",
    "fields",
    "symbol_search",
    "field_tokens",
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
assert palette.component_name == "CommandPalette"
assert dialog.component_name == "Dialog"
assert alert_dialog.component_name == "AlertDialog"
assert header.brand == brand
