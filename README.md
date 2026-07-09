# anylumino

`anylumino` is a small proof-of-concept library for creating anywidget widgets
that use Lumino for layout.

It targets the anywidget 0.11 AFM composition API: Python passes child
anywidgets as synced widget references, and the frontend resolves each child
with `host.getWidget(...)` before mounting it into a Lumino layout widget.

The main benefit is composition. `anylumino` lets a notebook author build
larger reusable widgets from existing anywidgets, anylumino controls,
charts, tables, and outputs. A composed widget can own its layout, state,
callbacks, and domain methods while still being an anywidget that can be nested
into another layout.

## Widgets

```python
from anylumino import Dropdown, IntSlider, SplitPanel, TabPanel, TextInput, Toolbar, VBox

dataset = TextInput(value="Greenhouse A", description="Dataset")
samples = IntSlider(value=120, min=25, max=250, description="Samples")
metric = Dropdown(options=["Temperature", "Humidity", "CO2"], value="Temperature")

tabs = TabPanel(
    {"trend": trend_figure, "summary": summary_table},
    titles={"trend": "Trend", "summary": "Summary"},
    height=460,
)

toolbar = Toolbar(
    [{"id": "refresh", "label": "Refresh"}],
    callbacks={"refresh": lambda _id: trend_panel.refresh()},
)

controls = VBox({"dataset": dataset, "samples": samples, "metric": metric})

SplitPanel({"controls": controls, "workspace": tabs}, orientation="vertical")
```

The current prototype provides:

- Layout widgets: public `LayoutWidget` base plus `TabPanel`, `BoxPanel`,
  `HBox`, `VBox`, `SplitPanel`, `DockPanel`, `AccordionPanel`,
  `StackedPanel`, `GridPanel`, and `ResponsivePanel`.
- Action widgets: `Toolbar`, `MenuBar`, and `CommandPalette`.
- Spectrum-backed controls: `Button`, `TextInput`, `TextArea`, `PasswordInput`,
  `Checkbox`, `Dropdown`, `ListBox`, `MultiSelect`, `RadioButtons`,
  `ToggleButton`, `ToggleButtons`, sliders, numeric inputs, progress bars,
  color picker, file upload metadata, media widgets, `Output`, `HTML`,
  `HTMLMath` as an `HTML` compatibility alias, and `Label`.
- Native controls: `DatePicker`, `TimePicker`, and `DatetimePicker`.
- Surfaces and display helpers: `FieldGroup`, `HelpText`, `ProgressCircle`,
  `Popover`, `Tooltip`, `Tray`, `DialogBox`, `Modal`, `ClearButton`,
  `CloseButton`, `InfieldButton`, `PickerButton`, `ColorHandle`, `ColorLoupe`,
  `OpacityCheckerboard`, `Table`, `Icon`, `UIIcon`, and `SpectrumElement`.
- `TextWidget`, a small helper used by tests and smoke notebooks.

All layout containers inherit from `LayoutWidget`, which provides keyed child
composition, owner access, dynamic mutation, and method forwarding.

This turns layout into an application structure, not only visual placement.
Children remain addressable by key, callbacks can interact with sibling
widgets, and larger components such as `FigurePanel`, `SampleReview`, or
`LabDashboard` can be reused across notebooks without relying on global
variables.

Layout widgets are resizable by drag and drop by default. Pass
`resizable=False` to hide the bottom-right resize handle. `SplitPanel` also
syncs Lumino split-handle changes back to its `sizes` trait.

Layout children can be declared with semantic keys. If `titles` is omitted for
a mapping, the titles default to those keys.

```python
tabs = TabPanel({"trend": trend_figure, "summary": summary_table})
tabs.select_key("summary")
tabs.selected_key
tabs.get_widget("trend")
```

If a child is a Python wrapper with a `.widget` anywidget view, anylumino renders
the view and keeps the wrapper as the keyed owner.

```python
tabs = TabPanel({"trend": trend_panel})
tabs.get_widget("trend")  # trend_panel.widget
tabs["trend"].refresh()
tabs.call_owner("trend", "refresh")
```

To add methods to a composed UI object, subclass a layout widget. The subclass
is still an anywidget and can be nested inside another layout:

```python
class FigurePanel(VBox):
    def __init__(self, figure):
        self.figure = figure
        super().__init__({"figure": figure})

    def refresh(self):
        update_figure(self.figure)


tabs = TabPanel({"trend": FigurePanel(figure)})
tabs["trend"].refresh()
```

`Toolbar`, `MenuBar`, and `CommandPalette` accept Python callbacks keyed by
action id, so controls can mutate another widget such as a figure after display.
Action widget icons render with Spectrum workflow icons. Use Spectrum icon names
such as `AddContent`, `RotateRight`, `Comment`, `GraphTrend`, `StepForward`,
`FullScreen`, and `HelpCircle`. Pass `icon_src` for a custom SVG/image icon and
`icon_size` for Spectrum icon sizing.

Most input controls are Spectrum-backed anywidgets and live in the Spectrum
family internally, so future component-library families can be added without
mixing renderer code. Date and time controls are browser-native controls in
`controls.py`. All controls can be placed inside Lumino layouts like any other
child widget and expose synced `value` traits plus normal traitlets observers.
Controls with an `icon` argument use the same Spectrum workflow icon fields as
action widgets. Use the `variant`, `quiet`, `spectrum_size`,
`spectrum_color`, and CSS custom properties exposed by Spectrum to align
Spectrum-backed controls with a design system.

Read an input widget's current value with `.value`. Use traitlets observers when
another widget should react to edits:

```python
dataset = TextInput(value="Greenhouse A", description="Dataset")
samples = IntSlider(value=120, min=25, max=250, description="Samples")

dataset.value
samples.value

samples.observe(lambda change: print(change["new"]), names="value")
```

Selection widgets also expose `.value`, and many expose `.index` for the
selected option position. Button-like widgets use callbacks because a click is
an event, not a persistent value.

Child-capable surface widgets accept keyed child anywidgets, support `show()`,
`hide()`, and `toggle()` for overlay-style state, and remain composable inside
Lumino layouts.

`Table` renders Spectrum table markup for structured row data. Pass mappings,
sequences, or scalar rows; use `row_key` when mappings contain a stable row id
such as an order id or symbol.

```python
from anylumino import Table

orders = Table(
    rows=[
        {"order_id": "O-1", "symbol": "AAPL", "qty": 10, "status": "NEW"},
        {"order_id": "O-2", "symbol": "MSFT", "qty": 5, "status": "PARTIAL"},
    ],
    columns={"order_id": "Order", "symbol": "Symbol", "qty": "Qty", "status": "Status"},
    row_key="order_id",
    selects="multiple",
    density="compact",
)

orders.prepend_row({"order_id": "O-0", "symbol": "AMD", "qty": 2, "status": "NEW"})
orders.append_row({"order_id": "O-3", "symbol": "NVDA", "qty": 1, "status": "NEW"})
orders.update_row("O-2", {"qty": 7, "status": "FILLED"})
orders.remove_row("O-1")
orders.set_rows(next_order_snapshot)
```

Each row helper assigns a new `rows` list, so displayed notebooks receive the
update through traitlets. `prepend_row` inserts before existing rows and
`append_row` inserts after existing rows.

Frontend assets are bundled into the Python package. Runtime notebooks do not
need CDN access for Lumino, Spectrum components, or the bundled workflow icons.
Use `icon_src` for custom local icons or data URI icons outside the bundled
workflow icon set.

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

Open `notebooks/plotly_tabs.py` for a focused dynamic-tab smoke test with
Plotly figures. Open `notebooks/plotly_dashboard.py` for a broader dashboard
that exercises the layout widgets, action callbacks, and Plotly figure updates
together. Open
`notebooks/itables_tabs.py` to see an `itables.widget.ITable` inside a tab with
controls that append rows to a pandas DataFrame and refresh the displayed table.
Open `notebooks/spectrum_remaining_components.py` for a smoke test of the
surface widgets, display helpers, and button variants.
