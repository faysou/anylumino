# anylumino

`anylumino` is a small proof-of-concept library for creating anywidget widgets
that use Lumino for layout.

It targets the anywidget 0.11 AFM composition API: Python passes child
anywidgets as synced widget references, and the frontend resolves each child
with `host.getWidget(...)` before mounting it into a Lumino layout widget.

## Tabs

```python
from anylumino import TabPanel

tabs = TabPanel(
    [chart_a.widget, chart_b.widget],
    titles=["Chart A", "Chart B"],
    height=460,
)
tabs
```

The current prototype provides a Lumino `TabPanel` wrapper and a simple
`TextWidget` helper used by tests and smoke checks.

## Development

```sh
uv sync --group dev
uv run pytest
uv run jupyter lab
```

Open `notebooks/lightweight_charts_tabs.py` in JupyterLab for a Jupytext smoke
test with basic child widgets and `lightweight-charts-python` chart widgets.
