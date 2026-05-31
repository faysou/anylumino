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
# # anylumino dashboard smoke test
#
# This notebook uses all anylumino layout and action widgets with
# `lightweight-charts-python`. Toolbar, menu, and command palette actions call
# Python callbacks that mutate chart widgets after the dashboard is displayed.

# %%
from __future__ import annotations

from pathlib import Path
import os
import sys

import pandas as pd

from anylumino import (
    AccordionPanel,
    BoxPanel,
    Button,
    Checkbox,
    CommandPalette,
    DockPanel,
    Dropdown,
    GridPanel,
    HBox,
    IntSlider,
    MenuBar,
    ResponsivePanel,
    SplitPanel,
    StackedPanel,
    TabPanel,
    TextInput,
    TextWidget,
    Toolbar,
    VBox,
)


def get_notebook_path() -> Path:
    try:
        from IPython import get_ipython

        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return Path(os.path.abspath(""))
    except (ImportError, NameError):
        pass
    return Path(__file__).resolve().parent


def find_nautilus_root() -> Path:
    notebook_path = get_notebook_path().resolve()
    return next(
        path for path in [notebook_path, *notebook_path.parents]
        if (path / "lightweight-charts-python").exists()
    )


nautilus_root = find_nautilus_root()
lightweight_charts_repo = nautilus_root / "lightweight-charts-python"
if str(lightweight_charts_repo) not in sys.path:
    sys.path.insert(0, str(lightweight_charts_repo))

from lightweight_charts_esistjosh import NotebookChart  # noqa: E402


data_path = lightweight_charts_repo / "examples" / "1_setting_data" / "ohlcv.csv"
stream_path = lightweight_charts_repo / "examples" / "2_live_data" / "next_ohlcv.csv"
data = pd.read_csv(data_path)
stream = pd.read_csv(stream_path)

# %%
status = TextWidget("Dashboard ready.")
help_text = TextWidget(
    "Use the toolbar, Chart menu, or command palette to create tabs, add markers, "
    "stream bars, change themes, and fit the active chart."
)
metric_symbol = TextWidget("Symbol: AAPL")
metric_rows = TextWidget(f"Rows: {len(data)}")
metric_action = TextWidget("Last action: none")
notes = TextWidget("Dock panel: command palette and notes can sit beside the main dashboard.")
layout_lab_intro = TextWidget("Layout lab: BoxPanel, HBox, VBox, GridPanel, ResponsivePanel, and SplitPanel.")
layout_lab_left = TextWidget("HBox child A")
layout_lab_right = TextWidget("HBox child B")
layout_lab_primary = TextWidget("BoxPanel stretch 2")
layout_lab_secondary = TextWidget("BoxPanel stretch 1")
layout_lab_wide = TextWidget("Responsive wide pane")
layout_lab_narrow = TextWidget("Responsive narrow pane")
symbol_input = TextInput(value="AAPL", description="Symbol")
rows_input = IntSlider(value=220, min=80, max=len(data), step=20, description="Rows")
theme_input = Dropdown(options=["dark", "light"], value="dark", description="Theme")
auto_fit_input = Checkbox(value=True, description="Auto fit")
apply_inputs_button = Button(description="Apply inputs", button_style="primary")

charts: dict[str, NotebookChart] = {}
chart_count = 0
stream_index = 0
theme_name = "dark"


def active_chart() -> NotebookChart:
    key = chart_tabs.selected_key
    if key is None:
        raise RuntimeError("No active chart tab")
    return charts[key]


def log(message: str) -> None:
    status.text = message
    metric_action.text = f"Last action: {message}"


def style_chart(chart: NotebookChart, theme: str) -> None:
    if theme == "light":
        chart.layout(background_color="#f8fafc", text_color="#172033", font_size=12)
        chart.grid(True, True, color="rgba(100, 116, 139, 0.18)", style="dotted")
        chart.candle_style(
            up_color="rgba(5, 150, 105, 0.95)",
            down_color="rgba(220, 38, 38, 0.95)",
            border_up_color="rgba(5, 150, 105, 0.95)",
            border_down_color="rgba(220, 38, 38, 0.95)",
            wick_up_color="rgba(5, 150, 105, 0.95)",
            wick_down_color="rgba(220, 38, 38, 0.95)",
        )
        chart.watermark("anylumino", color="rgba(14, 116, 144, 0.12)", font_size=34)
    else:
        chart.layout(background_color="#0b1020", text_color="#e5edf5", font_size=12)
        chart.grid(True, True, color="rgba(148, 163, 184, 0.16)", style="dotted")
        chart.candle_style(
            up_color="rgba(45, 212, 191, 0.95)",
            down_color="rgba(251, 113, 133, 0.95)",
            border_up_color="rgba(45, 212, 191, 0.95)",
            border_down_color="rgba(251, 113, 133, 0.95)",
            wick_up_color="rgba(45, 212, 191, 0.95)",
            wick_down_color="rgba(251, 113, 133, 0.95)",
        )
        chart.watermark("anylumino", color="rgba(249, 115, 22, 0.14)", font_size=34)
    chart.legend(True, text=f"{theme.title()} theme")


def create_chart(title: str, rows: int = 220) -> NotebookChart:
    chart = NotebookChart(width="100%", height="100%", toolbox=False)
    chart.set(data.tail(rows).reset_index(drop=True))
    style_chart(chart, theme_name)
    chart.fit()
    return chart


def add_chart_tab(_action_id: str = "new_chart") -> None:
    global chart_count

    chart_count += 1
    key = f"chart-{chart_count}"
    title = f"Chart {chart_count}"
    rows = min(len(data), 120 + chart_count * 40)
    chart = create_chart(title, rows=rows)
    charts[key] = chart
    chart_tabs.add_tab(chart, title, key=key, select=True)
    metric_rows.text = f"Rows: {rows}"
    log(f"Created {title}")


def apply_inputs(_button: Button | None = None) -> None:
    global theme_name

    chart = active_chart()
    rows = int(rows_input.value)
    theme_name = str(theme_input.value)
    chart.set(data.tail(rows).reset_index(drop=True))
    style_chart(chart, theme_name)
    if auto_fit_input.value:
        chart.fit()
    metric_symbol.text = f"Symbol: {symbol_input.value}"
    metric_rows.text = f"Rows: {rows}"
    log(f"Applied inputs to {chart_tabs.selected_key}")


def add_marker(_action_id: str = "marker") -> None:
    chart = active_chart()
    chart.marker(text="anylumino action")
    log("Added marker to active chart")


def add_sma(_action_id: str = "sma") -> None:
    chart = active_chart()
    source = data.tail(180).reset_index(drop=True)
    line = chart.create_line("SMA 20", color="rgba(250, 204, 21, 0.95)", width=2)
    line.set(
        pd.DataFrame(
            {
                "time": source["date"],
                "SMA 20": source["close"].rolling(20).mean(),
            }
        ).dropna()
    )
    log("Added SMA 20 line")


def fit_chart(_action_id: str = "fit") -> None:
    active_chart().fit()
    log("Fit active chart")


def stream_bar(_action_id: str = "stream") -> None:
    global stream_index

    row = stream.iloc[stream_index % len(stream)]
    stream_index += 1
    active_chart().update(row)
    log(f"Streamed bar {stream_index}")


def toggle_theme(_action_id: str = "theme") -> None:
    global theme_name

    theme_name = "light" if theme_name == "dark" else "dark"
    for chart in charts.values():
        style_chart(chart, theme_name)
    log(f"Switched to {theme_name} theme")


def show_help(_action_id: str = "help") -> None:
    side_stack.select(1)
    log("Showing help panel")


def show_status(_action_id: str = "status") -> None:
    side_stack.select(0)
    log("Showing status panel")


def screenshot_chart(_action_id: str = "screenshot") -> None:
    path = Path("/tmp/anylumino_dashboard_chart.png")
    active_chart().screenshot(path)
    log(f"Screenshot written to {path}")


chart_count = 1
primary_chart = create_chart("Chart 1")
charts["chart-1"] = primary_chart
apply_inputs_button.on_click(apply_inputs)
chart_tabs = TabPanel(
    {"chart-1": primary_chart},
    titles={"chart-1": "Chart 1"},
    selected_index=0,
    width="100%",
    height="100%",
)

# %%
toolbar = Toolbar(
    [
        {"id": "new_chart", "label": "New chart"},
        {"id": "marker", "label": "Marker"},
        {"id": "sma", "label": "SMA"},
        {"id": "stream", "label": "Stream"},
        {"id": "fit", "label": "Fit"},
        {"id": "theme", "label": "Theme"},
    ],
    callbacks={
        "new_chart": add_chart_tab,
        "marker": add_marker,
        "sma": add_sma,
        "stream": stream_bar,
        "fit": fit_chart,
        "theme": toggle_theme,
    },
)

menu = MenuBar(
    [
        {
            "label": "Chart",
            "items": [
                {"id": "new_chart", "label": "New chart tab"},
                {"id": "fit", "label": "Fit active chart"},
                {"id": "screenshot", "label": "Screenshot"},
            ],
        },
        {
            "label": "Actions",
            "items": [
                {"id": "marker", "label": "Add marker"},
                {"id": "sma", "label": "Add SMA 20"},
                {"id": "stream", "label": "Stream one bar"},
                {"id": "theme", "label": "Toggle theme"},
            ],
        },
        {
            "label": "Panels",
            "items": [
                {"id": "status", "label": "Show status"},
                {"id": "help", "label": "Show help"},
            ],
        },
    ],
    callbacks={
        "new_chart": add_chart_tab,
        "fit": fit_chart,
        "screenshot": screenshot_chart,
        "marker": add_marker,
        "sma": add_sma,
        "stream": stream_bar,
        "theme": toggle_theme,
        "status": show_status,
        "help": show_help,
    },
)

commands = CommandPalette(
    [
        {"id": "new_chart", "label": "New chart tab", "category": "Chart"},
        {"id": "marker", "label": "Add marker", "category": "Chart"},
        {"id": "sma", "label": "Add SMA 20", "category": "Chart"},
        {"id": "stream", "label": "Stream one bar", "category": "Data"},
        {"id": "fit", "label": "Fit active chart", "category": "View"},
        {"id": "theme", "label": "Toggle theme", "category": "View"},
        {"id": "status", "label": "Show status", "category": "Panels"},
        {"id": "help", "label": "Show help", "category": "Panels"},
    ],
    callbacks={
        "new_chart": add_chart_tab,
        "marker": add_marker,
        "sma": add_sma,
        "stream": stream_bar,
        "fit": fit_chart,
        "theme": toggle_theme,
        "status": show_status,
        "help": show_help,
    },
)

side_stack = StackedPanel(
    {"status": status, "help": help_text},
    titles={"status": "Status", "help": "Help"},
    height=150,
)
metrics = GridPanel(
    {
        "symbol": metric_symbol,
        "rows": metric_rows,
        "last-action": metric_action,
    },
    columns="1fr",
    rows="auto auto auto",
    gap=8,
    height=160,
)
input_controls = VBox(
    {
        "symbol": symbol_input,
        "rows": rows_input,
        "theme": theme_input,
        "auto-fit": auto_fit_input,
        "apply": apply_inputs_button,
    },
    spacing=6,
    height=210,
)
side_accordion = AccordionPanel(
    {"status": side_stack, "metrics": metrics, "inputs": input_controls},
    titles={"status": "Status", "metrics": "Metrics", "inputs": "Inputs"},
    height="100%",
)
chart_app = GridPanel(
    {"menu": menu, "toolbar": toolbar, "charts": chart_tabs},
    columns="1fr",
    rows="34px 44px minmax(0, 1fr)",
    gap=0,
    areas=[
        {"row": "1 / 2", "column": "1 / 2"},
        {"row": "2 / 3", "column": "1 / 2"},
        {"row": "3 / 4", "column": "1 / 2"},
    ],
    height="100%",
)
main = SplitPanel(
    {"charts": chart_app, "controls": side_accordion},
    titles={"charts": "Charts", "controls": "Controls"},
    orientation="horizontal",
    spacing=8,
    sizes=[0.76, 0.24],
    height=560,
)
layout_lab = VBox(
    {
        "intro": layout_lab_intro,
        "hbox": HBox({"left": layout_lab_left, "right": layout_lab_right}, height=62),
        "box": BoxPanel(
            {"primary": layout_lab_primary, "secondary": layout_lab_secondary},
            direction="left-to-right",
            stretches=[2, 1],
            height=74,
        ),
        "responsive": ResponsivePanel(
            {"wide": layout_lab_wide, "narrow": layout_lab_narrow},
            breakpoint=700,
            wide_direction="left-to-right",
            narrow_direction="top-to-bottom",
            height=104,
        ),
    },
    spacing=8,
    stretches=[0, 0, 0, 1],
    height="100%",
)
dock = DockPanel(
    {"commands": commands, "layout-lab": layout_lab, "notes": notes},
    titles={"commands": "Commands", "layout-lab": "Layout lab", "notes": "Notes"},
    mode="split-right",
    height=280,
)
dashboard = VBox(
    {
        "app": SplitPanel(
            {"main": main, "dock": dock},
            orientation="vertical",
            sizes=[0.68, 0.32],
        )
    },
    height=920,
)

dashboard

# %%
