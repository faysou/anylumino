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
status = ax.Text("astryx status: ready", text_type="supporting", color="secondary")


def record_click(_button):
    clicks["count"] += 1
    status.text = f"astryx status: clicked {clicks['count']}"


title = ax.Text("Astryx component render check", text_type="large", weight="semibold")
subtitle = ax.Text(
    "Notebook-safe Astryx controls, display widgets, generated lists, tables, and composed layouts.",
    text_type="supporting",
    color="secondary",
)
breadcrumbs = ax.Breadcrumbs(
    [
        {"label": "Notebook", "href": "#"},
        {"label": "Astryx", "href": "#"},
        {"label": "Components", "current": True},
    ],
    variant="supporting",
)
connected = ax.StatusDot("Connected", variant="success", pulsing=True)
badge = ax.Badge("Live", variant="success")
progress = ax.ProgressBar(
    58, label="Render coverage", variant="success", value_label=True
)
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


symbol = ax.TextInput(
    value="AAPL", label="Symbol", placeholder="Ticker", clear=True, width="220px"
)
notes = ax.TextArea(
    value="Watch opening auction imbalance.", label="Notes", rows=3, width="320px"
)
limit = ax.NumberInput(
    value=250, label="Order limit", min=0, max=1000, step=10, units="sh", width="180px"
)
risk = ax.Slider(
    value=42, label="Risk budget", min=0, max=100, value_display="text", width="260px"
)
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
    trigger_display="badges",
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
field_tokens = ax.Tokenizer(
    ["Bid", "Ask", "Last", "Size", "Venue"],
    value=["Bid", "Ask"],
    label="Tokenized fields",
    width="280px",
)
trade_date = ax.DateInput(value="2026-07-09", label="Trade date", width="180px")
trade_time = ax.TimeInput(value="14:30", label="Time", hour_format="24h", width="160px")
enabled = ax.Checkbox(value=True, label="Enabled")
stream = ax.Switch(value=False, label="Stream")
pinned = ax.ToggleButton(value=True, label="Pinned")
density = ax.SegmentedControl(
    ["Compact", "Standard", "Detailed"],
    value="Standard",
    label="Density",
    size="sm",
)
mode = ax.RadioList(
    ["Auto", "Manual"], value="Auto", label="Mode", orientation="horizontal"
)
streams = ax.CheckboxList(
    ["Quotes", "Trades", "Depth"], value=["Quotes", "Trades"], label="Streams"
)


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
    columns={"minWidth": 320, "repeat": "fit"},
    gap=4,
    width="100%",
)

wrapped_symbol = ax.Field(
    ax.TextInput(value="NVDA", label="Symbol", label_hidden=True, width="180px"),
    label="Wrapped symbol",
    description="Field wrapper around a custom input",
    width="220px",
)
grouped_qty = ax.InputGroup(
    ax.NumberInput(value=100, label="Quantity", label_hidden=True),
    label="Quantity",
    suffix="sh",
    width="220px",
)
calendar = ax.Calendar("2026-07-09", week_numbers=True)
file_input = ax.FileInput(
    label="Upload CSV", accept=".csv", mode="input", width="240px"
)
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
        {
            "key": "symbol",
            "header": "Symbol",
            "width": {"kind": "proportional", "value": 1},
        },
        {"key": "side", "header": "Side", "width": {"kind": "pixel", "value": 90}},
        {
            "key": "status",
            "header": "Status",
            "width": {"kind": "proportional", "value": 1},
        },
    ],
    density="compact",
    dividers="grid",
    hover=True,
)
watchlist = ax.List(
    [
        {"label": "Opening imbalance", "description": "Auction monitor"},
        {"label": "Venue latency", "description": "P95 execution path"},
        {"label": "Risk checks", "description": "Pre-trade guardrails"},
    ],
    header="Watchlist",
    dividers=True,
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
tabs = ax.TabList(
    ["Summary", "Orders", "Risk"], value="Summary", layout="fill", divider=True
)
button_group = ax.ButtonGroup(
    [
        {"label": "Apply", "variant": "primary"},
        {"label": "Stage"},
        {"label": "Cancel", "variant": "ghost"},
    ],
    label="Order actions",
    callbacks=[record_click],
)
view_toggle = ax.ToggleButtonGroup(
    [("Grid", "grid"), ("List", "list")],
    value="grid",
    label="View mode",
    size="sm",
)
more_button = ax.IconButton(
    "Refresh view", icon="rotate", variant="ghost", callbacks=[record_click]
)
dropdown = ax.DropdownMenu(
    [
        {"label": "Refresh", "value": "refresh"},
        {"label": "Export", "value": "export"},
    ],
    label="Actions",
    callbacks=[record_click],
)
more_menu = ax.MoreMenu(
    ["Edit", "Duplicate", "Archive"], label="Row actions", callbacks=[record_click]
)


data_section = ax.Grid(
    {
        "orders": ax.Card({"table": orders}, padding=2, width="100%"),
        "list": ax.Card({"watchlist": watchlist}, padding=3),
        "metadata": ax.Card({"metadata": metadata}, padding=3),
        "tabs": ax.Card(
            {
                "tabs": tabs,
                "actions": ax.Stack(
                    {
                        "group": button_group,
                        "view": view_toggle,
                        "menu": dropdown,
                        "more_menu": more_menu,
                        "more": more_button,
                    },
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
avatar_group = ax.AvatarGroup(
    ["Ada Lovelace", "Grace Hopper", "Katherine Johnson"],
    overflow_count=2,
    size="small",
)
icon = ax.Icon("check", size="md", color="success")
token = ax.Token("sim", color="blue")
kbd = ax.Kbd("mod+enter")
skeleton = ax.Skeleton(width=160, height=16)
spinner = ax.Spinner(size="sm", label="Loading")
empty = ax.EmptyState(
    "No rejected orders",
    description="Rejected order events will appear here.",
    compact=True,
)
code = ax.CodeBlock(
    "order = {'symbol': 'AAPL', 'side': 'BUY'}", language="python", line_numbers=False
)
inline_code = ax.Code("order_id")
markdown = ax.Markdown(
    "**Markdown** with `inline code` and a compact list:\n\n- quotes\n- trades",
    density="compact",
)
quote = ax.Blockquote(
    "Design system widgets can compose cleanly inside Jupyter outputs."
)
timestamp = ax.Timestamp(
    "2026-07-09T14:30:00Z", format="system_date_time", timezone=True
)
thumbnail = ax.Thumbnail(label="preview.png", loading=True)
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
popover = ax.Popover(
    ax.Text("Compact popover content"), ax.Button("Open"), label="Details"
)
details = ax.Collapsible(
    ax.Markdown("Verbose diagnostics can live here."),
    trigger="Diagnostics",
    default_open=False,
)
palette = ax.CommandPalette(
    [
        {"id": "refresh", "label": "Refresh", "auxiliaryData": {"group": "Data"}},
        {"id": "export", "label": "Export CSV", "auxiliaryData": {"group": "Files"}},
    ],
    value="refresh",
    width=420,
)
dialog = ax.Dialog(
    ax.Text("Inline dialog content stays inside the notebook output."),
    open=True,
    width=360,
)
alert_dialog = ax.AlertDialog(
    "Confirm action",
    "This inline preview uses the alert dialog surface.",
    action_label="Confirm",
)
preview_image = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='360'%3E%3Crect width='640' height='360' fill='%230057b8'/%3E%3C/svg%3E"
overlay = ax.Overlay(
    ax.Card(
        {
            "preview": ax.Thumbnail(
                label="Market preview", src=preview_image, alt="Blue market preview"
            )
        },
        padding=2,
        width=220,
    ),
    ax.Button("Quick view", variant="ghost"),
    show_on="always",
    position="bottom",
    align="center",
)
lightbox = ax.Lightbox(
    [
        {
            "src": preview_image,
            "alt": "Blue lightbox preview",
            "caption": "Inline image preview",
        },
        {
            "src": "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
            "alt": "Flower video preview",
            "type": "video",
            "caption": "Native video controls",
        },
    ],
    zoom=True,
)
open_lightbox = ax.Button(
    "Open lightbox",
    callbacks=[lambda _widget: lightbox.show()],
)


visuals = ax.Grid(
    {
        "identity": ax.Card(
            {
                "row": ax.Stack(
                    {
                        "avatar": avatar,
                        "group": avatar_group,
                        "icon": icon,
                        "token": token,
                        "kbd": kbd,
                        "time": timestamp,
                    },
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
    },
    columns={"minWidth": 300, "repeat": "fit"},
    gap=3,
    width="100%",
)


# The structure card is much taller than the visuals cards, so it gets its own
# full-width row instead of leaving a blank cell beside it.
structure = ax.Card(
    {
        "form": form_layout,
        "calendar": calendar,
        "outline": outline,
        "tree": tree,
        "overlays": ax.Stack(
            {
                "tooltip": tooltip,
                "hover": hover,
                "popover": popover,
                "overlay": overlay,
                "open_lightbox": open_lightbox,
                "lightbox": lightbox,
            },
            direction="horizontal",
            gap=2,
            wrap="wrap",
        ),
        "details": details,
    },
    padding=3,
    width="100%",
)


# The palette and dialogs are wider than a responsive grid cell, so they get a
# full-width section of their own rather than clipping inside one.
surfaces = ax.Card(
    {
        "palette": palette,
        "dialog": dialog,
        "alert": alert_dialog,
    },
    padding=3,
    width="100%",
)


order_pages = ax.Pagination(1, total_items=120, page_size=20, page_size_options=[10, 20, 50])
preview_carousel = ax.Carousel(
    {
        "first": ax.Card({"caption": ax.Text("Panel one")}, padding=3, width=220),
        "second": ax.Card({"caption": ax.Text("Panel two")}, padding=3, width=220),
        "third": ax.Card({"caption": ax.Text("Panel three")}, padding=3, width=220),
    },
    snap=True,
)
row_menu = ax.ContextMenu(
    [("Copy row", "copy"), ("Export row", "export")],
    ax.Card({"hint": ax.Text("Right-click for row actions")}, padding=3, width="100%"),
    action_callbacks=[lambda _widget, action: record_click(_widget)],
)
order_filter = ax.PowerSearch(
    {
        "name": "orders",
        "fields": [
            {
                "key": "symbol",
                "label": "Symbol",
                "operators": [{"key": "is", "label": "is"}, {"key": "isNot", "label": "is not"}],
            },
            {
                "key": "side",
                "label": "Side",
                "operators": [{"key": "is", "label": "is"}],
            },
        ],
    },
    filters=[{"field": "symbol", "operator": "is", "value": "AAPL"}],
    label="Filter orders",
    clear=True,
)

navigation = ax.Card(
    {
        "filter": order_filter,
        "carousel": preview_carousel,
        "menu": row_menu,
        "pages": order_pages,
    },
    padding=3,
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
                "structure": structure,
                "surfaces": surfaces,
                "navigation": navigation,
                "status": status,
            },
            brand=brand,
            gap=3,
        ),
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
assert view_toggle.value == "grid"
assert form_layout.component_name == "FormLayout"
assert wrapped_symbol.component_name == "Field"
assert wrapped_symbol.get_widget(0).value == "NVDA"
assert grouped_qty.component_name == "InputGroup"
assert grouped_qty.get_widget(0).value == 100
assert calendar.component_name == "Calendar"
assert dropdown.component_name == "DropdownMenu"
assert more_menu.component_name == "MoreMenu"
assert outline.component_name == "Outline"
assert tree.component_name == "TreeList"
assert tooltip.child_keys == ["trigger"]
assert popover.child_keys == ["trigger", "content"]
assert overlay.child_keys == ["base", "content"]
assert lightbox.props["media"][1]["type"] == "video"
assert palette.component_name == "CommandPalette"
assert dialog.component_name == "Dialog"
assert alert_dialog.component_name == "AlertDialog"
assert header.brand == brand
assert status.brand == brand
assert structure.child_keys == [
    "form",
    "calendar",
    "outline",
    "tree",
    "overlays",
    "details",
]
assert surfaces.child_keys == ["palette", "dialog", "alert"]
assert navigation.child_keys == ["filter", "carousel", "menu", "pages"]
assert order_pages.value == 1
assert order_pages.props["pageSizeOptions"] == [10, 20, 50]
assert preview_carousel.child_keys == ["first", "second", "third"]
assert row_menu.props["items"][0] == {"label": "Copy row", "value": "copy"}
assert order_filter.value == [{"field": "symbol", "operator": "is", "value": "AAPL"}]

# %%

# %%
