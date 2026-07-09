# anylumino

`anylumino` is a small proof-of-concept library for creating anywidget widgets
that use Lumino for layout and Astryx for notebook UI components.

It targets the anywidget 0.11 AFM composition API: Python passes child
anywidgets as synced widget references, and the frontend resolves each child
with `host.getWidget(...)` before mounting it into a Lumino layout widget or an
Astryx component slot.

The main benefit is composition. `anylumino` lets a notebook author build
larger reusable widgets from existing anywidgets, Astryx controls, charts,
tables, and outputs. A composed widget can own its layout, state, callbacks,
and domain methods while still being an anywidget that can be nested into
another layout.

## Quick start

```python
import anylumino as al

brand = al.AstryxBrand(
    "desk",
    **{
        "color-accent": ("#0057b8", "#79b8ff"),
        "color-background-card": ("#ffffff", "#111827"),
        "color-text-primary": ("#111827", "#f9fafb"),
        "radius-container": "8px",
    },
)

status = al.TextWidget("Ready")

orders = al.AstryxTable(
    rows=[
        {"order_id": "O-1", "symbol": "AAPL", "qty": 10, "status": "NEW"},
        {"order_id": "O-2", "symbol": "MSFT", "qty": 5, "status": "PARTIAL"},
    ],
    columns={"order_id": "Order", "symbol": "Symbol", "qty": "Qty", "status": "Status"},
    row_key="order_id",
    selects="multiple",
    sortable=True,
    sort_key="symbol",
    width="100%",
)

controls = al.AstryxTheme(
    {
        "heading": al.AstryxStack(
            {
                "title": al.AstryxHeading("Orders", level=3),
                "badge": al.AstryxBadge("Live", variant="success"),
            },
            direction="horizontal",
            gap=2,
            align="center",
        ),
        "symbol": al.AstryxTypeahead(
            ["AAPL", "MSFT", "NVDA"],
            value="AAPL",
            label="Symbol",
        ),
        "fields": al.AstryxTokenizer(
            ["Bid", "Ask", "Last", "Size"],
            value=["Bid", "Ask"],
            label="Fields",
        ),
        "refresh": al.AstryxButton(
            "Refresh",
            variant="primary",
            callbacks=[lambda _button: setattr(status, "value", "Refreshed")],
        ),
        "orders": orders,
    },
    brand=brand,
    mode="system",
    gap=3,
)

al.SplitPanel(
    {"controls": controls, "status": status},
    orientation="vertical",
    sizes=[0.8, 0.2],
    height=560,
)
```

## What it provides

- Layout widgets: public `LayoutWidget` base plus `TabPanel`, `BoxPanel`,
  `HBox`, `VBox`, `ScrollBox`, `SplitPanel`, `DockPanel`, `AccordionPanel`,
  `StackedPanel`, `GridPanel`, and `ResponsivePanel`.
- Astryx component wrappers for notebook UI: buttons, text, headings, badges,
  cards, stacks, grids, forms, fields, tabs, segmented controls, selectors,
  checkboxes, radio lists, sliders, date/time inputs, banners, status dots,
  progress bars, code, Markdown, tooltips, popovers, inline dialogs, static
  search inputs, command palettes, and tables.
- Astryx table helpers: normalized rows and columns, optional checkbox
  selection, sorting, row append/prepend/update/remove helpers, and Python
  callbacks for selection and sort changes.
- Reusable Astryx theming with `AstryxBrand` and `AstryxTheme`, so notebooks can
  define shared colors, radii, and component treatment once.
- Action widgets: `AstryxToolbar`, `AstryxDropdownMenu`, `AstryxMoreMenu`, and
  `AstryxCommandPalette` for notebook-safe commands.
- `TextWidget`, a small helper used by tests and smoke notebooks.

All layout containers inherit from `LayoutWidget`, which provides keyed child
composition, owner access, dynamic mutation, and method forwarding.

This turns layout into an application structure, not only visual placement.
Children remain addressable by key, callbacks can interact with sibling
widgets, and larger components such as `OrderDashboard`, `FigurePanel`, or
`SampleReview` can be reused across notebooks without relying on global
variables.

## Layout composition

Layout widgets are resizable by drag and drop by default. Pass
`resizable=False` to hide the bottom-right resize handle. `SplitPanel` also
syncs Lumino split-handle changes back to its `sizes` trait.

Layout children can be declared with semantic keys. If `titles` is omitted for
a mapping, the titles default to those keys.

```python
tabs = al.TabPanel({"orders": orders, "logs": al.TextWidget("No events")})
tabs.select_key("orders")
tabs.selected_key
tabs.get_widget("logs")
```

If a child is a Python wrapper with a `.widget` anywidget view, anylumino renders
the view and keeps the wrapper as the keyed owner.

```python
tabs = al.TabPanel({"trend": trend_panel})
tabs.get_widget("trend")  # trend_panel.widget
tabs["trend"].refresh()
tabs.call_owner("trend", "refresh")
```

To add methods to a composed UI object, subclass a layout widget. The subclass
is still an anywidget and can be nested inside another layout:

```python
class OrderDashboard(al.VBox):
    def __init__(self, rows):
        self.table = al.AstryxTable(
            rows,
            row_key="order_id",
            selects="multiple",
            sortable=True,
        )
        super().__init__({"table": self.table})

    def replace_orders(self, rows):
        self.table.set_rows(rows)


tabs = al.TabPanel({"orders": OrderDashboard(order_rows)})
tabs["orders"].replace_orders(next_order_rows)
```

## Astryx widgets

Astryx widgets are the UI family for notebook-facing controls. They use the
`Astryx*` prefix so notebook component code stays explicit:

```python
form = al.AstryxFormLayout(
    {
        "symbol": al.AstryxTextInput(value="AAPL", label="Symbol"),
        "quantity": al.AstryxNumberInput(value=100, label="Quantity", min=1),
        "side": al.AstryxSegmentedControl(
            ["Buy", "Sell"],
            value="Buy",
            label="Side",
        ),
        "routing": al.AstryxSelector(
            ["Smart", "Primary", "Dark"],
            value="Smart",
            label="Routing",
        ),
        "urgent": al.AstryxCheckbox(value=False, label="Urgent"),
    }
)
```

Read an input widget's current value with `.value`. Use traitlets observers
when another widget should react to edits:

```python
symbol = al.AstryxTextInput(value="AAPL", label="Symbol")
quantity = al.AstryxNumberInput(value=100, label="Quantity")

symbol.value
quantity.value

symbol.observe(lambda change: print(change["new"]), names="value")
```

Button-like widgets use callbacks because a click is an event, not a persistent
value.

```python
status = al.TextWidget("Ready")
button = al.AstryxButton(
    "Submit",
    variant="primary",
    callbacks=[lambda _button: setattr(status, "value", "Submitted")],
)
```

## Astryx tables

`AstryxTable` renders structured row data with optional checkbox selection and
sorting. Pass mappings, sequences, or scalar rows; use `row_key` when mappings
contain a stable row id such as an order id or symbol.

```python
orders = al.AstryxTable(
    rows=[
        {"order_id": "O-1", "symbol": "AAPL", "qty": 10, "status": "NEW"},
        {"order_id": "O-2", "symbol": "MSFT", "qty": 5, "status": "PARTIAL"},
    ],
    columns={"order_id": "Order", "symbol": "Symbol", "qty": "Qty", "status": "Status"},
    row_key="order_id",
    selects="multiple",
    sortable=True,
    sort_key="symbol",
)

orders.prepend_row({"order_id": "O-0", "symbol": "AMD", "qty": 2, "status": "NEW"})
orders.append_row({"order_id": "O-3", "symbol": "NVDA", "qty": 1, "status": "NEW"})
orders.update_row("O-2", {"qty": 7, "status": "FILLED"})
orders.remove_row("O-1")
orders.set_rows(next_order_snapshot)
```

Each row helper assigns a new `rows` list, so displayed notebooks receive the
update through traitlets. `prepend_row` inserts before existing rows and
`append_row` inserts after existing rows. Leave `selects=""` for no checkbox
column, use `selects="single"` for one selected row, or use
`selects="multiple"` for multi-row selection.

## Theming

Use `AstryxBrand` and `AstryxTheme` for small reusable notebook theme
overrides:

```python
brand = al.AstryxBrand(
    "desk",
    **{
        "color-accent": ("#0057b8", "#79b8ff"),
        "color-background-card": ("#ffffff", "#111827"),
        "radius-container": "8px",
    },
)

panel = al.AstryxTheme(
    {"button": al.AstryxButton("Run"), "status": al.AstryxBadge("Ready")},
    brand=brand,
    mode="system",
    gap=2,
)
```

`AstryxTheme` propagates the brand to nested Astryx children because every
anywidget child is mounted in its own frontend root. See
`docs/astryx_brand_theme.md` for runtime `defineTheme()` themes,
precompiled `AstryxBuiltTheme` CSS themes, and the workflow for defining new
Astryx themes. That document also describes the frontend style injection,
deduplication, and JupyterLab testing workflow for theme changes.

## Assets

Frontend assets are bundled into the Python package. Runtime notebooks do not
need CDN access for Lumino, Astryx, or the bundled workflow icons.

## Development

```sh
uv sync --group dev
npm ci
npm run build
uv run pytest
uv run jupyter lab
```

Build and browse the documentation site:

```sh
make docs-preview
```

This opens `http://127.0.0.1:4200/` automatically. The rendered site is static
under `web/_site`; use `make docs-serve` to rebuild it and serve that static
output.

Open `notebooks/astryx_components_smoke.py` for the broad Astryx component
smoke test. Open `notebooks/astryx_table.py` for focused table selection,
sorting, and row-helper examples. Open `notebooks/plotly_tabs.py` and
`notebooks/plotly_dashboard.py` for Lumino layout patterns with Plotly figures.
Open `notebooks/itables_tabs.py` to see an `itables.widget.ITable` inside a tab
with controls that append rows to a pandas DataFrame and refresh the displayed
table.
