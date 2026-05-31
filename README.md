# anylumino

`anylumino` is a small proof-of-concept library for creating anywidget widgets
that use Lumino for layout.

It targets the anywidget 0.11 AFM composition API: Python passes child
anywidgets as synced widget references, and the frontend resolves each child
with `host.getWidget(...)` before mounting it into a Lumino layout widget.

## Widgets

```python
from anylumino import Dropdown, IntSlider, SplitPanel, TabPanel, TextInput, Toolbar, VBox

symbol = TextInput(value="AAPL", description="Symbol")
rows = IntSlider(value=200, min=50, max=500, description="Rows")
interval = Dropdown(options=["1m", "5m", "1h"], value="1m", description="Interval")

tabs = TabPanel(
    {"chart-a": chart_a.widget, "chart-b": chart_b.widget},
    titles={"chart-a": "Chart A", "chart-b": "Chart B"},
    height=460,
)

toolbar = Toolbar(
    [{"id": "fit", "label": "Fit"}],
    callbacks={"fit": lambda _id: chart_a.fit()},
)

controls = VBox({"symbol": symbol, "rows": rows, "interval": interval})

SplitPanel({"controls": controls, "charts": tabs}, orientation="vertical")
```

The current prototype provides:

- Layout widgets: public `LayoutWidget` base plus `TabPanel`, `BoxPanel`,
  `HBox`, `VBox`, `SplitPanel`, `DockPanel`, `AccordionPanel`,
  `StackedPanel`, `GridPanel`, and `ResponsivePanel`.
- Action widgets: `Toolbar`, `MenuBar`, and `CommandPalette`.
- Input controls re-exported from ipywidgets: `Button`, `TextInput`, `TextArea`,
  `PasswordInput`, `Checkbox`, `Dropdown`, `ListBox`, `MultiSelect`,
  `RadioButtons`, `ToggleButton`, `ToggleButtons`, sliders, numeric inputs,
  progress bars, date/time pickers, color picker, file upload, media widgets,
  `Output`, `HTML`, `HTMLMath`, and `Label`.
- `TextWidget`, a small helper used by tests and smoke notebooks.

All layout containers inherit from `LayoutWidget`, which provides keyed child
composition, owner access, dynamic mutation, and method forwarding.

Layout widgets are resizable by drag and drop by default. Pass
`resizable=False` to hide the bottom-right resize handle. `SplitPanel` also
syncs Lumino split-handle changes back to its `sizes` trait.

Layout children can be declared with semantic keys. If `titles` is omitted for
a mapping, the titles default to those keys.

```python
tabs = TabPanel({"price": price_chart.widget, "volume": volume_chart.widget})
tabs.select_key("volume")
tabs.selected_key
tabs.get_widget("price")
```

If a child is a Python wrapper with a `.widget` anywidget view, anylumino renders
the view and keeps the wrapper as the keyed owner.

```python
tabs = TabPanel({"price": price_chart})
tabs.get_widget("price")  # price_chart.widget
tabs["price"].fit()
tabs.call_owner("price", "fit")
```

To add methods to a composed UI object, subclass a layout widget. The subclass
is still an anywidget and can be nested inside another layout:

```python
class ChartPanel(VBox):
    def __init__(self, chart):
        self.chart = chart
        super().__init__({"chart": chart.widget})

    def fit(self):
        self.chart.fit()


tabs = TabPanel({"price": ChartPanel(chart)})
tabs["price"].fit()
```

`Toolbar`, `MenuBar`, and `CommandPalette` accept Python callbacks keyed by
action id, so controls can mutate another widget such as a chart after display.

The input controls are ipywidgets classes exposed through anylumino. They reuse
Jupyter's existing `@jupyter-widgets/controls` frontend and can be placed inside
Lumino layouts like any other child widget.

## Development

```sh
uv sync --group dev
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

Open `notebooks/lightweight_charts_tabs.py` for a focused dynamic-tab smoke
test. Open `notebooks/lightweight_charts_dashboard.py` for a broader dashboard
that exercises the layout widgets, action callbacks, and
`lightweight-charts-python` chart operations together. Open
`notebooks/itables_tabs.py` to see an `itables.widget.ITable` inside a tab with
controls that append rows to a pandas DataFrame and refresh the displayed table.
