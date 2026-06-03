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
# # anylumino Plotly dashboard smoke test
#
# This notebook uses the anylumino layout and action widgets with Plotly
# `FigureWidget` children. Toolbar, menu, and command palette actions call
# Python callbacks that mutate figures after the dashboard is displayed.

# %%
from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go

from anylumino import (
    AccordionPanel,
    Badge,
    BoxPanel,
    Button,
    Checkbox,
    CommandPalette,
    DockPanel,
    Dropdown,
    GridPanel,
    HBox,
    IntSlider,
    Meter,
    MenuBar,
    ResponsivePanel,
    ScrollBox,
    SplitPanel,
    StackedPanel,
    TabPanel,
    TextInput,
    TextWidget,
    Toolbar,
    VBox,
)


def make_sensor_frame(rows: int = 240, phase: float = 0.0) -> pd.DataFrame:
    records = []
    for index in range(rows):
        hour = index / 4
        records.append(
            {
                "sample": index,
                "temperature": 21.5 + math.sin(hour / 4 + phase) * 2.4 + math.cos(hour / 9) * 0.6,
                "humidity": 48 + math.cos(hour / 5 + phase) * 7 + math.sin(hour / 11) * 2,
                "co2": 430 + math.sin(hour / 6 + phase) * 34 + index * 0.08,
            }
        )
    return pd.DataFrame(records)


data = make_sensor_frame()


# %%
status = TextWidget("Dashboard ready.")
help_text = TextWidget(
    "Use the toolbar, Data menu, or command palette to create tabs, add notes, "
    "append samples, change themes, and focus the active figure."
)
metric_dataset = TextWidget("Dataset: greenhouse")
metric_rows = TextWidget(f"Samples: {len(data)}")
metric_action = TextWidget("Last action: none")
state_badge = Badge(value="Ready", variant="positive", icon="InfoCircle")
completion_meter = Meter(value=75, description="Review coverage", variant="informative", readout=True)
notes = TextWidget("Dock panel: command palette and notes can sit beside the main dashboard.")
accordion_status = TextWidget("Accordion demo status section.")
accordion_metrics = TextWidget("Accordion demo metrics section.")
layout_lab_intro = TextWidget("Layout lab: BoxPanel, HBox, VBox, GridPanel, ResponsivePanel, and SplitPanel.")
layout_lab_left = TextWidget("HBox child A")
layout_lab_right = TextWidget("HBox child B")
layout_lab_primary = TextWidget("BoxPanel stretch 2")
layout_lab_secondary = TextWidget("BoxPanel stretch 1")
layout_lab_wide = TextWidget("Responsive wide pane")
layout_lab_narrow = TextWidget("Responsive narrow pane")
dataset_input = TextInput(value="greenhouse", description="Dataset")
samples_input = IntSlider(value=180, min=60, max=len(data), step=20, description="Samples")
metric_input = Dropdown(options=["temperature", "humidity", "co2"], value="temperature", description="Metric")
theme_input = Dropdown(options=["light", "dark"], value="light", description="Theme")
auto_focus_input = Checkbox(value=True, description="Auto focus")
apply_inputs_button = Button(description="Apply inputs", variant="accent", icon="CheckmarkCircle")

figures: dict[str, go.FigureWidget] = {}
figure_count = 0
sample_offset = 0
theme_name = "light"
active_figure_key = "figure-1"


def active_figure() -> go.FigureWidget:
    key = figure_tabs.selected_key
    if key not in figures:
        key = active_figure_key
    if key not in figures:
        raise RuntimeError("No active figure tab")
    return figures[key]


def log(message: str) -> None:
    status.text = message
    metric_action.text = f"Last action: {message}"
    state_badge.value = "Updated"


def template_for_theme(theme: str) -> str:
    return "plotly_dark" if theme == "dark" else "plotly_white"


def style_figure(figure: go.FigureWidget, theme: str) -> None:
    if theme == "dark":
        paper_bgcolor = "#111827"
        plot_bgcolor = "#172033"
        font_color = "#f8fafc"
        grid_color = "#334155"
    else:
        paper_bgcolor = "#ffffff"
        plot_bgcolor = "#ffffff"
        font_color = "#172033"
        grid_color = "#d8dee9"

    figure.update_layout(
        template=template_for_theme(theme),
        paper_bgcolor=paper_bgcolor,
        plot_bgcolor=plot_bgcolor,
        font={"color": font_color},
        margin={"l": 48, "r": 24, "t": 54, "b": 42},
        legend={"orientation": "h", "y": 1.08},
    )
    figure.update_xaxes(gridcolor=grid_color, zerolinecolor=grid_color)
    figure.update_yaxes(gridcolor=grid_color, zerolinecolor=grid_color)


def frame_slice(rows: int, metric: str) -> pd.DataFrame:
    return data.tail(rows)[["sample", metric]].reset_index(drop=True)


def create_figure(title: str, rows: int = 180, metric: str = "temperature") -> go.FigureWidget:
    frame = frame_slice(rows, metric)
    figure = go.FigureWidget()
    figure.add_scatter(
        x=frame["sample"],
        y=frame[metric],
        mode="lines+markers",
        name=metric,
    )
    figure.update_layout(title=title, height=430, xaxis_title="Sample", yaxis_title=metric.title())
    style_figure(figure, theme_name)
    return figure


def refresh_figure(figure: go.FigureWidget, rows: int, metric: str) -> None:
    frame = frame_slice(rows, metric)
    with figure.batch_update():
        figure.data[0].x = frame["sample"]
        figure.data[0].y = frame[metric]
        figure.data[0].name = metric
        figure.layout.yaxis.title = metric.title()
    style_figure(figure, theme_name)


def add_figure_tab(_action_id: str = "new_figure") -> None:
    global active_figure_key
    global figure_count

    figure_count += 1
    key = f"figure-{figure_count}"
    title = f"Figure {figure_count}"
    rows = min(len(data), 100 + figure_count * 30)
    figure = create_figure(title, rows=rows, metric=str(metric_input.value))
    figures[key] = figure
    figure_tabs.add_tab(figure, title, key=key, select=True)
    active_figure_key = key
    metric_rows.text = f"Samples: {rows}"
    log(f"Created {title}")


def apply_inputs(_button: Button | None = None) -> None:
    global active_figure_key
    global theme_name

    active_figure_key = figure_tabs.selected_key or active_figure_key
    figure = active_figure()
    rows = int(samples_input.value)
    metric = str(metric_input.value)
    theme_name = str(theme_input.value)
    refresh_figure(figure, rows, metric)
    if auto_focus_input.value:
        focus_figure()
    metric_dataset.text = f"Dataset: {dataset_input.value}"
    metric_rows.text = f"Samples: {rows}"
    log(f"Applied inputs to {figure_tabs.selected_key}")


def add_note(_action_id: str = "note") -> None:
    sync_active_figure_key()
    figure = active_figure()
    y_value = float(figure.data[0].y[-1])
    x_value = int(figure.data[0].x[-1])
    figure.add_annotation(x=x_value, y=y_value, text="review", showarrow=True, arrowhead=2)
    log("Added note to active figure")


def add_average(_action_id: str = "average") -> None:
    sync_active_figure_key()
    figure = active_figure()
    values = list(map(float, figure.data[0].y))
    window = 12
    averaged = [
        sum(values[max(0, index - window + 1) : index + 1]) / len(values[max(0, index - window + 1) : index + 1])
        for index in range(len(values))
    ]
    figure.add_scatter(x=figure.data[0].x, y=averaged, mode="lines", name="rolling average")
    log("Added rolling average")


def focus_figure(_action_id: str = "focus") -> None:
    sync_active_figure_key()
    figure = active_figure()
    figure.update_xaxes(autorange=True)
    figure.update_yaxes(autorange=True)
    log("Focused active figure")


def append_sample(_action_id: str = "append") -> None:
    global active_figure_key
    global sample_offset

    active_figure_key = figure_tabs.selected_key or active_figure_key
    figure = active_figure()
    sample_offset += 1
    next_x = int(figure.data[0].x[-1]) + 1
    next_y = float(figure.data[0].y[-1]) + math.sin(sample_offset / 2) * 0.35
    with figure.batch_update():
        figure.data[0].x = [*figure.data[0].x, next_x]
        figure.data[0].y = [*figure.data[0].y, next_y]
    log(f"Appended sample {next_x}")


def toggle_theme(_action_id: str = "theme") -> None:
    global theme_name

    theme_name = "dark" if theme_name == "light" else "light"
    for figure in figures.values():
        style_figure(figure, theme_name)
    theme_input.value = theme_name
    log(f"Switched to {theme_name} theme")


def sync_active_figure_key(_change: object | None = None) -> None:
    global active_figure_key

    key = figure_tabs.selected_key
    if key in figures:
        active_figure_key = key


def show_help(_action_id: str = "help") -> None:
    side_stack.select(1)
    log("Showing help panel")


def show_status(_action_id: str = "status") -> None:
    side_stack.select(0)
    log("Showing status panel")


figure_count = 1
primary_figure = create_figure("Figure 1")
figures["figure-1"] = primary_figure
apply_inputs_button.on_click(apply_inputs)
figure_tabs = TabPanel(
    {"figure-1": primary_figure},
    titles={"figure-1": "Figure 1"},
    selected_index=0,
    width="100%",
    height="100%",
)
figure_tabs.observe(sync_active_figure_key, names="selected_index")


# %%
toolbar = Toolbar(
    [
        {"id": "new_figure", "label": "New figure", "icon": "AddContent"},
        {"id": "note", "label": "Note", "icon": "Comment"},
        {"id": "average", "label": "Average", "icon": "GraphTrend"},
        {"id": "append", "label": "Append", "icon": "StepForward"},
        {"id": "focus", "label": "Focus", "icon": "FullScreen"},
        {"id": "theme", "label": "Theme", "icon": "Light"},
    ],
    callbacks={
        "new_figure": add_figure_tab,
        "note": add_note,
        "average": add_average,
        "append": append_sample,
        "focus": focus_figure,
        "theme": toggle_theme,
    },
)

menu = MenuBar(
    [
        {
            "label": "Data",
            "items": [
                {"id": "new_figure", "label": "New figure tab", "icon": "AddContent"},
                {"id": "focus", "label": "Focus active figure", "icon": "FullScreen"},
            ],
        },
        {
            "label": "Actions",
            "items": [
                {"id": "note", "label": "Add note", "icon": "Comment"},
                {"id": "average", "label": "Add rolling average", "icon": "GraphTrend"},
                {"id": "append", "label": "Append sample", "icon": "StepForward"},
                {"id": "theme", "label": "Toggle theme", "icon": "Light"},
            ],
        },
        {
            "label": "Panels",
            "items": [
                {"id": "status", "label": "Show status", "icon": "InfoCircle"},
                {"id": "help", "label": "Show help", "icon": "HelpCircle"},
            ],
        },
    ],
    callbacks={
        "new_figure": add_figure_tab,
        "focus": focus_figure,
        "note": add_note,
        "average": add_average,
        "append": append_sample,
        "theme": toggle_theme,
        "status": show_status,
        "help": show_help,
    },
)

commands = CommandPalette(
    [
        {"id": "new_figure", "label": "New figure tab", "category": "Data", "icon": "AddContent"},
        {"id": "note", "label": "Add note", "category": "Data", "icon": "Comment"},
        {"id": "average", "label": "Add rolling average", "category": "Data", "icon": "GraphTrend"},
        {"id": "append", "label": "Append sample", "category": "Data", "icon": "StepForward"},
        {"id": "focus", "label": "Focus active figure", "category": "View", "icon": "FullScreen"},
        {"id": "theme", "label": "Toggle theme", "category": "View", "icon": "Light"},
        {"id": "status", "label": "Show status", "category": "Panels", "icon": "InfoCircle"},
        {
            "id": "help",
            "label": "Show help",
            "category": "Panels",
            "icon": "HelpCircle",
        },
    ],
    callbacks={
        "new_figure": add_figure_tab,
        "note": add_note,
        "average": add_average,
        "append": append_sample,
        "focus": focus_figure,
        "theme": toggle_theme,
        "status": show_status,
        "help": show_help,
    },
)

side_stack = StackedPanel(
    {"status": status, "help": help_text},
    titles={"status": "Status", "help": "Help"},
    height=92,
)
metrics = GridPanel(
    {
        "dataset": metric_dataset,
        "samples": metric_rows,
        "last-action": metric_action,
        "state": state_badge,
        "coverage": completion_meter,
    },
    columns="1fr",
    rows="auto auto auto auto auto",
    gap=8,
    height=190,
)
input_controls = ScrollBox(
    {
        "dataset": dataset_input,
        "samples": samples_input,
        "metric": metric_input,
        "theme": theme_input,
        "auto-focus": auto_focus_input,
        "apply": apply_inputs_button,
    },
    spacing=8,
    height=430,
    child_min_height=56,
)
control_panel = VBox(
    {
        "inputs": input_controls,
        "status": side_stack,
        "metrics": metrics,
    },
    spacing=12,
    stretches=[1, 0, 0],
    height="100%",
)
accordion_demo = AccordionPanel(
    {"status": accordion_status, "metrics": accordion_metrics},
    titles={"status": "Status", "metrics": "Metrics"},
    height="100%",
)
figure_app = GridPanel(
    {"menu": menu, "toolbar": toolbar, "figures": figure_tabs},
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
    {"controls": control_panel, "figures": figure_app},
    titles={"figures": "Figures", "controls": "Controls"},
    orientation="horizontal",
    spacing=8,
    sizes=[0.42, 0.58],
    height=720,
)
layout_lab = VBox(
    {
        "intro": layout_lab_intro,
        "hbox": HBox(
            {"left": layout_lab_left, "right": layout_lab_right},
            spacing=12,
            scroll=True,
            child_min_width=180,
            height=62,
        ),
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
    {"commands": commands, "layout-lab": layout_lab, "accordion": accordion_demo, "notes": notes},
    titles={"commands": "Commands", "layout-lab": "Layout lab", "accordion": "Accordion", "notes": "Notes"},
    mode="split-right",
    height=280,
)
dashboard = VBox(
    {
        "app": SplitPanel(
            {"main": main, "dock": dock},
            orientation="vertical",
            sizes=[0.68, 0.32],
            height="100%",
        )
    },
    stretches=[1],
    height=1040,
)

dashboard

# %%
