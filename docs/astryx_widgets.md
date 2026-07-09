# Astryx notebook widgets

Astryx widgets are the component family for notebook UIs in `anylumino`. They
use the `Astryx*` prefix so the UI surface stays explicit and easy to scan in
notebook code.

Use Astryx widgets when a notebook needs a polished JupyterLab-friendly
interface with forms, selectors, tables, status surfaces, inline dialogs, or a
shared brand identity.

## Dashboard pattern

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
    width="100%",
)

controls = al.AstryxTheme(
    {
        "header": al.AstryxStack(
            {
                "title": al.AstryxHeading("Orders", level=3),
                "badge": al.AstryxBadge("Live", variant="success"),
            },
            direction="horizontal",
            align="center",
            gap=2,
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
        "density": al.AstryxSegmentedControl(
            ["Compact", "Standard"],
            value="Standard",
            label="Density",
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
    {"workspace": controls, "status": status},
    orientation="vertical",
    sizes=[0.85, 0.15],
    height=560,
)
```

## Component groups

### Foundation and theme

Use these when creating reusable wrappers, applying shared styling, or reaching
for a component that does not yet have a dedicated Python class.

- `AstryxWidget`
- `AstryxComponent`
- `AstryxBrand`
- `AstryxTheme`

### Typography and content

Use these for headings, body copy, rendered Markdown, code, links, avatars, and
small semantic content.

- `AstryxText`
- `AstryxHeading`
- `AstryxMarkdown`
- `AstryxCode`
- `AstryxCodeBlock`
- `AstryxBlockquote`
- `AstryxKbd`
- `AstryxLink`
- `AstryxCitation`
- `AstryxTimestamp`
- `AstryxThumbnail`
- `AstryxAvatar`
- `AstryxAvatarGroup`
- `AstryxIcon`

### Layout containers

Use these to arrange Astryx content inside a notebook output before placing the
result in a Lumino layout.

- `AstryxStack`
- `AstryxGrid`
- `AstryxCenter`
- `AstryxSection`
- `AstryxCard`
- `AstryxClickableCard`
- `AstryxAspectRatio`
- `AstryxDivider`
- `AstryxCollapsible`

### Forms and direct inputs

Use these for direct value entry and form composition.

- `AstryxFormLayout`
- `AstryxField`
- `AstryxFieldStatus`
- `AstryxInputGroup`
- `AstryxTextInput`
- `AstryxTextArea`
- `AstryxNumberInput`
- `AstryxSlider`
- `AstryxCheckbox`
- `AstryxSwitch`
- `AstryxToggleButton`
- `AstryxDateInput`
- `AstryxDateRangeInput`
- `AstryxDateTimeInput`
- `AstryxTimeInput`
- `AstryxCalendar`
- `AstryxFileInput`

### Selection and search

Use these when users choose from predefined options or searchable static
sources.

- `AstryxSelector`
- `AstryxMultiSelector`
- `AstryxSegmentedControl`
- `AstryxRadioList`
- `AstryxCheckboxList`
- `AstryxTypeahead`
- `AstryxTokenizer`

### Actions and menus

Use these for command surfaces and button-like interactions.

- `AstryxButton`
- `AstryxIconButton`
- `AstryxButtonGroup`
- `AstryxToolbar`
- `AstryxDropdownMenu`
- `AstryxMoreMenu`
- `AstryxCommandPalette`

### Feedback and status

Use these to show state, progress, loading placeholders, or empty results.

- `AstryxBadge`
- `AstryxStatusDot`
- `AstryxProgressBar`
- `AstryxSpinner`
- `AstryxSkeleton`
- `AstryxToken`
- `AstryxBanner`
- `AstryxEmptyState`

### Overlays and previews

Use these for notebook-safe contextual surfaces. Dialog wrappers default to
inline rendering so they stay inside the output area.

- `AstryxTooltip`
- `AstryxHoverCard`
- `AstryxPopover`
- `AstryxDialog`
- `AstryxAlertDialog`

### Navigation and data

Use these for structured navigation and data-heavy notebook views.

- `AstryxBreadcrumbs`
- `AstryxTabList`
- `AstryxList`
- `AstryxMetadataList`
- `AstryxOutline`
- `AstryxTreeList`
- `AstryxTable`

## State and callbacks

Input widgets expose a synced `.value` trait:

```python
symbol = al.AstryxTextInput(value="AAPL", label="Symbol")
quantity = al.AstryxNumberInput(value=100, label="Quantity")

symbol.value
quantity.value

symbol.observe(lambda change: print(change["new"]), names="value")
```

Button-style widgets use callbacks because a click is an event:

```python
status = al.TextWidget("Ready")
submit = al.AstryxButton(
    "Submit",
    variant="primary",
    callbacks=[lambda _button: setattr(status, "value", "Submitted")],
)
```

## Table selection and sorting

`AstryxTable` keeps selection and sort state in synced traits:

```python
orders = al.AstryxTable(
    rows=[
        {"order_id": "O-1", "symbol": "AAPL", "qty": 10},
        {"order_id": "O-2", "symbol": "MSFT", "qty": 5},
    ],
    columns={"order_id": "Order", "symbol": "Symbol", "qty": "Qty"},
    row_key="order_id",
    selects="multiple",
    sortable=True,
)

orders.selected
orders.sort_key
orders.sort_direction
```

Use `selects=""` for no checkbox column, `selects="single"` for one selected
row, or `selects="multiple"` for checkbox multi-selection.

## Notebook-safe overlays

Dialog-style components default to inline rendering:

```python
preview = al.AstryxDialog(
    al.AstryxText("Inline dialog content stays inside the notebook output."),
    open=True,
    width=360,
)

confirm = al.AstryxAlertDialog(
    "Confirm action",
    "This inline preview uses the alert dialog surface.",
    action_label="Confirm",
)
```

Inline rendering avoids modal focus-management conflicts inside Jupyter output
areas. Use non-inline dialogs only after validating the surrounding notebook
environment.

## Related notebooks

- `notebooks/astryx_components_smoke.py` covers the broad component family.
- `notebooks/astryx_table.py` focuses on table selection, sorting, and row
  helper behavior.
