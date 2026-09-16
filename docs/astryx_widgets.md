# Astryx notebook widgets

Astryx widgets are the component family for notebook UIs in `anylumino`. They
live in the `anylumino.astryx` namespace so the UI surface stays explicit and
easy to scan in notebook code.

Use Astryx widgets when a notebook needs a polished JupyterLab-friendly
interface with forms, selectors, tables, status surfaces, inline dialogs, or a
shared brand identity.

Useful appearance and behavior options are keyword-only constructor arguments
with Python snake-case names, so they appear in signatures, IDE completion, and
the API docstrings. Unmodeled JSON-safe upstream options remain available
through `**props`; React nodes, refs, render functions, and JavaScript-only test
props are not promoted to the Python API. See the
[Astryx component documentation](https://astryx.atmeta.com/components) for the
upstream component reference.

## Dashboard pattern

```python
import anylumino as al
import anylumino.astryx as ax

brand = ax.Brand(
    "desk",
    **{
        "color-accent": ("#0057b8", "#79b8ff"),
        "color-background-card": ("#ffffff", "#111827"),
        "color-text-primary": ("#111827", "#f9fafb"),
        "radius-container": "8px",
    },
)

status = ax.Text("Ready")

orders = ax.Table(
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

controls = ax.Theme(
    {
        "header": ax.Stack(
            {
                "title": ax.Heading("Orders", level=3),
                "badge": ax.Badge("Live", variant="success"),
            },
            direction="horizontal",
            align="center",
            gap=2,
        ),
        "symbol": ax.Typeahead(
            ["AAPL", "MSFT", "NVDA"],
            value="AAPL",
            label="Symbol",
        ),
        "fields": ax.Tokenizer(
            ["Bid", "Ask", "Last", "Size"],
            value=["Bid", "Ask"],
            label="Fields",
        ),
        "density": ax.SegmentedControl(
            ["Compact", "Standard"],
            value="Standard",
            label="Density",
        ),
        "refresh": ax.Button(
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

The groups below follow how a notebook UI is put together: composition first,
then content, inputs, actions, feedback, overlays, and data. Every class lives
in the `anylumino.astryx` namespace; the module column says where its API
reference page is.

| Group                   | API module           |
| ----------------------- | -------------------- |
| Foundation and theme    | `base`               |
| Layout panels           | `layout`             |
| Layout containers       | `surfaces`           |
| Typography and content  | `inputs`, `data`     |
| Forms and direct inputs | `inputs`, `surfaces` |
| Selection and search    | `inputs`, `surfaces` |
| Actions and menus       | `inputs`, `surfaces` |
| Feedback and status     | `data`               |
| Overlays and previews   | `surfaces`           |
| Navigation and data     | `surfaces`, `data`   |

### Foundation and theme

Use these to define a shared brand, apply a theme to a subtree, or wrap an
Astryx component that has no dedicated Python class yet.

- `Widget`
- `Component`
- `Brand`
- `BuiltTheme`
- `Theme`

### Layout panels

Use these for the structure of a notebook UI: tabs, one-at-a-time panels,
collapsible sections, scrolling regions, resizable panes, and layouts that
reflow with the available width. They mirror the Lumino layout widgets with
the same keyed child API, so `select_key`, `add_widget`, and `remove_widget`
work the same way, while rendering with Astryx styling.

- `TabPanel`
- `StackedPanel`
- `AccordionPanel`
- `ScrollBox`
- `SplitPanel`
- `ResponsivePanel`

```python
tabs = ax.TabPanel({"orders": orders, "fills": fills}, size="sm")
tabs.select_key("fills")

workspace = ax.SplitPanel(
    {"controls": controls, "chart": figure},
    sizes=[0.3, 0.7],
    height=480,
)
```

`TabPanel` and `StackedPanel` mount a child the first time it is shown and keep
it mounted, hidden, afterwards, so a Plotly figure keeps its state across tab
switches. `SplitPanel` syncs drags back to its `sizes` trait as fractions.

### Layout containers

Use these to arrange content inside a panel or a notebook output.

- `Stack`
- `Grid`
- `Center`
- `Section`
- `Card`
- `ClickableCard`
- `SelectableCard`
- `AspectRatio`
- `Divider`
- `Collapsible`
- `Carousel`

### Typography and content

Use these for headings, body copy, rendered Markdown, code, links, avatars, and
small semantic content.

- `Text`
- `Heading`
- `Markdown`
- `Code`
- `CodeBlock`
- `Blockquote`
- `Kbd`
- `Link`
- `Citation`
- `Timestamp`
- `Thumbnail`
- `Avatar`
- `AvatarGroup`
- `Icon`

### Forms and direct inputs

Use these for direct value entry and form composition.

- `FormLayout`
- `Field`
- `FieldStatus`
- `InputGroup`
- `TextInput`
- `TextArea`
- `NumberInput`
- `Slider`
- `LogSlider`
- `SelectionSlider`
- `Checkbox`
- `Switch`
- `ToggleButton`
- `ToggleButtonGroup`
- `DateInput`
- `DateRangeInput`
- `DateTimeInput`
- `TimeInput`
- `Calendar`
- `FileInput`

### Selection and search

Use these when users choose from predefined options or searchable sources.

- `Selector`
- `MultiSelector`
- `SegmentedControl`
- `RadioList`
- `CheckboxList`
- `Typeahead`
- `Tokenizer`
- `PowerSearch`

### Actions and menus

Use these for command surfaces and button-like interactions.

- `Button`
- `IconButton`
- `ButtonGroup`
- `Toolbar`
- `DropdownMenu`
- `ContextMenu`
- `MoreMenu`
- `CommandPalette`

### Feedback and status

Use these to show state, progress, loading placeholders, or empty results.

- `Badge`
- `StatusDot`
- `ProgressBar`
- `Spinner`
- `Skeleton`
- `Token`
- `Banner`
- `EmptyState`

### Overlays and previews

Use these for notebook-safe contextual surfaces. Dialog wrappers default to
inline rendering so they stay inside the output area.

- `Tooltip`
- `HoverCard`
- `Popover`
- `Overlay`
- `Lightbox`
- `Dialog`
- `AlertDialog`

### Navigation and data

Use these for structured navigation and data-heavy notebook views.

- `Breadcrumbs`
- `TabList`
- `List`
- `MetadataList`
- `Outline`
- `TreeList`
- `Pagination`
- `Table`

## Input labels

`TextInput`, `Selector`, `MultiSelector`, `Slider`, `LogSlider`, and
`SelectionSlider` accept `label_position="top"`
(the default) or `label_position="left"` for compact forms. Both positions retain
the control's accessible label. Descriptions and validation messages stay with
the control. The horizontal layout stacks at viewport widths of 480 px or less.

```python
quantity = ax.Slider(10, label="Quantity", label_position="left", min=0, max=100)
```

Use the same `label_width` on sibling controls to align their inputs. For example,
`label_position="left", label_width=80` reserves an 80 px label column. CSS sizes
such as `"6rem"` also work; omitting the width fits each label to its text.

## State and callbacks

Input widgets expose a synced `.value` trait:

```python
symbol = ax.TextInput(value="AAPL", label="Symbol")
quantity = ax.NumberInput(value=100, label="Quantity")

symbol.value
quantity.value

symbol.observe(lambda change: print(change["new"]), names="value")
```

Button-style widgets use callbacks because a click is an event:

```python
status = ax.Text("Ready")
submit = ax.Button(
    "Submit",
    variant="primary",
    callbacks=[lambda _button: setattr(status, "value", "Submitted")],
)
```

Menus and grouped actions also accept `action_callbacks`. Each callback
receives `(widget, action_value)`, preserving the selected item identifier.

## Table selection and sorting

`Table` keeps selection and sort state in synced traits:

```python
orders = ax.Table(
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
preview = ax.Dialog(
    ax.Text("Inline dialog content stays inside the notebook output."),
    open=True,
    width=360,
)

confirm = ax.AlertDialog(
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
- `notebooks/astryx_layout_panels.py` shows each layout panel with
  Python-driven selection, open sections, and split sizes.
- `notebooks/astryx_table.py` focuses on table selection, sorting, and row
  helper behavior.
