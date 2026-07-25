from datetime import datetime
from inspect import signature
from pathlib import Path

import pytest

from anylumino import astryx as ax
from anylumino import spectrum as sx
import traitlets as t

from anylumino import (
    AccordionPanel,
    BoxPanel,
    CommandPalette,
    ComponentWidget,
    DatePicker,
    DatetimePicker,
    GridPanel,
    HBox,
    DockPanel,
    LayoutWidget,
    MenuBar,
    ResponsivePanel,
    ScrollBox,
    SplitPanel,
    StackedPanel,
    TabPanel,
    TextWidget,
    Toolbar,
    VBox,
)
from anylumino.common import static_asset


def _asset_path(asset: object) -> Path:
    path = getattr(asset, "_path", None)
    assert isinstance(path, Path)
    return path


def test_tab_panel_serializes_child_widgets_as_anywidget_refs() -> None:
    first = TextWidget("First")
    second = TextWidget("Second")

    panel = TabPanel([first, second], titles=["One", "Two"], selected_index=1)

    assert panel.get_state(
        key=["widgets", "child_keys", "titles", "selected_index"]
    ) == {
        "widgets": [f"anywidget:{first.model_id}", f"anywidget:{second.model_id}"],
        "child_keys": ["widget-1", "widget-2"],
        "titles": ["One", "Two"],
        "selected_index": 1,
    }


def test_layout_widgets_share_public_base_class() -> None:
    panels = [
        TabPanel({"child": TextWidget("Child")}),
        BoxPanel({"child": TextWidget("Child")}),
        HBox({"child": TextWidget("Child")}),
        VBox({"child": TextWidget("Child")}),
        ScrollBox({"child": TextWidget("Child")}),
        SplitPanel({"child": TextWidget("Child")}),
        DockPanel({"child": TextWidget("Child")}),
        AccordionPanel({"child": TextWidget("Child")}),
        StackedPanel({"child": TextWidget("Child")}),
        GridPanel({"child": TextWidget("Child")}),
        ResponsivePanel({"child": TextWidget("Child")}),
    ]

    assert [isinstance(panel, LayoutWidget) for panel in panels] == [True] * len(panels)
    assert [panel["child"].value for panel in panels] == ["Child"] * len(panels)


def test_text_widget_uses_value_without_text_alias() -> None:
    widget = TextWidget("Status")

    widget.value = "Updated"

    assert widget.value == "Updated"
    assert widget.get_state(key=["value"]) == {"value": "Updated"}
    with pytest.raises(AttributeError):
        _ = widget.text


def test_tab_panel_size_inputs_are_normalized_to_css_values() -> None:
    panel = TabPanel([TextWidget("Only")], width=0.5, height=240)

    assert panel.width == "50%"
    assert panel.height == "240px"


def test_tab_panel_is_resizable_by_default() -> None:
    panel = TabPanel()

    assert panel.resizable is True


def test_composed_widget_resizing_can_be_disabled() -> None:
    panel = SplitPanel([TextWidget("A"), TextWidget("B")], resizable=False)

    assert panel.resizable is False


def test_layout_widgets_can_fit_content() -> None:
    panel = VBox({"child": TextWidget("Child")}, fit_content=True)

    assert panel.fit_content is True
    assert panel.get_state(key=["fit_content"]) == {"fit_content": True}


def test_dict_children_use_keys_as_default_titles() -> None:
    first = TextWidget("First")
    second = TextWidget("Second")

    panel = TabPanel({"price": first, "volume": second})

    assert panel.child_keys == ["price", "volume"]
    assert panel.titles == ["price", "volume"]
    assert panel["price"] is first
    assert panel.get_widget("volume") is second


def test_dict_children_accept_title_mapping() -> None:
    first = TextWidget("First")
    second = TextWidget("Second")

    panel = SplitPanel(
        {"price": first, "volume": second},
        titles={"price": "Price", "volume": "Volume"},
    )

    assert panel.child_keys == ["price", "volume"]
    assert panel.titles == ["Price", "Volume"]


def test_list_children_accept_explicit_keys() -> None:
    first = TextWidget("First")
    second = TextWidget("Second")

    panel = GridPanel([first, second], keys=["left", "right"])

    assert panel.child_keys == ["left", "right"]
    assert panel.get_index("right") == 1
    assert panel.get_key(0) == "left"


def test_widget_keys_must_be_unique() -> None:
    with pytest.raises(ValueError, match="widget keys must be unique"):
        TabPanel([TextWidget("A"), TextWidget("B")], keys=["same", "same"])


def test_keyed_selection_tracks_selected_child() -> None:
    first = TextWidget("First")
    second = TextWidget("Second")
    panel = TabPanel({"first": first, "second": second})

    panel.select_key("second")

    assert panel.selected_index == 1
    assert panel.selected_key == "second"
    assert panel.selected_widget is second
    assert panel.selected_owner is second


def test_keyed_mutation_methods_add_rename_and_remove_children() -> None:
    panel = TabPanel()
    child = TextWidget("Price")

    panel.add("price", child, title="Price", select=True)
    panel.rename_widget("price", "Main price")
    removed = panel.remove_widget("price")

    assert removed is child
    assert panel.widgets == []
    assert panel.child_keys == []
    assert panel.titles == []
    assert panel.selected_index == 0


def test_wrapper_children_keep_owner_and_render_widget_separate() -> None:
    class ChartWrapper:
        def __init__(self) -> None:
            self.widget = TextWidget("Chart")
            self.calls: list[str] = []

        def fit(self) -> str:
            self.calls.append("fit")
            return "fit-ok"

    wrapper = ChartWrapper()
    panel = TabPanel({"chart": wrapper})

    assert panel.get_widget("chart") is wrapper.widget
    assert panel.get_owner("chart") is wrapper
    assert panel["chart"] is wrapper
    assert panel.call_owner("chart", "fit") == "fit-ok"
    assert wrapper.calls == ["fit"]


def test_tab_panel_requires_matching_titles() -> None:
    with pytest.raises(ValueError, match="titles must be empty"):
        TabPanel([TextWidget("Only")], titles=["One", "Two"])


def test_tab_panel_rejects_non_widget_children() -> None:
    panel = TabPanel()

    with pytest.raises(t.TraitError):
        panel.widgets = ["not a widget"]


def test_add_tab_appends_widget_and_title() -> None:
    panel = TabPanel()
    child = TextWidget("Added")

    panel.add_tab(child, "Added tab")

    assert panel.widgets == [child]
    assert panel.titles == ["Added tab"]


def test_add_tab_can_select_appended_widget() -> None:
    first = TextWidget("First")
    panel = TabPanel([first], titles=["First"])
    child = TextWidget("Added")

    panel.add_tab(child, "Added tab", select=True)

    assert panel.widgets == [first, child]
    assert panel.titles == ["First", "Added tab"]
    assert panel.selected_index == 1


def test_box_panel_exposes_lumino_direction_and_stretches() -> None:
    panel = BoxPanel(
        [TextWidget("Left"), TextWidget("Right")],
        direction="top-to-bottom",
        stretches=[1, 3],
        height=0.5,
    )

    assert panel.layout_kind == "box"
    assert panel.direction == "top-to-bottom"
    assert panel.stretches == [1, 3]
    assert panel.height == "50%"


def test_vbox_uses_vertical_box_direction() -> None:
    panel = VBox([TextWidget("Top")])

    assert panel.direction == "top-to-bottom"


def test_hbox_scroll_defaults_to_horizontal_axis() -> None:
    panel = HBox([TextWidget("A"), TextWidget("B")], scroll=True)

    assert panel.scroll_x is True
    assert panel.scroll_y is False
    assert panel.child_min_width == "220px"
    assert panel.child_min_height == "0px"


def test_vbox_scroll_defaults_to_vertical_axis() -> None:
    panel = VBox([TextWidget("A"), TextWidget("B")], scroll=True)

    assert panel.scroll_x is False
    assert panel.scroll_y is True
    assert panel.child_min_width == "0px"
    assert panel.child_min_height == "44px"


def test_box_panel_scroll_axes_and_child_min_sizes_can_be_overridden() -> None:
    panel = HBox(
        [TextWidget("A"), TextWidget("B")],
        scroll=True,
        scroll_y=True,
        child_min_width=180,
        child_min_height=72,
    )

    assert panel.scroll_x is True
    assert panel.scroll_y is True
    assert panel.child_min_width == "180px"
    assert panel.child_min_height == "72px"


def test_scroll_box_is_vertical_and_scrollable_by_default() -> None:
    panel = ScrollBox([TextWidget("A"), TextWidget("B")])

    assert panel.direction == "top-to-bottom"
    assert panel.scroll_x is False
    assert panel.scroll_y is True
    assert panel.height == "420px"


def test_split_panel_tracks_orientation_and_sizes() -> None:
    panel = SplitPanel(
        [TextWidget("A"), TextWidget("B")],
        orientation="vertical",
        sizes=[0.25, 0.75],
    )

    assert panel.layout_kind == "split"
    assert panel.orientation == "vertical"
    assert panel.sizes == [0.25, 0.75]


def test_dock_panel_tracks_dock_mode() -> None:
    panel = DockPanel([TextWidget("A"), TextWidget("B")], mode="tab-after")

    assert panel.layout_kind == "dock"
    assert panel.mode == "tab-after"


def test_accordion_panel_is_a_composed_layout() -> None:
    panel = AccordionPanel([TextWidget("A")], titles=["Section"])

    assert panel.layout_kind == "accordion"
    assert panel.titles == ["Section"]


def test_stacked_panel_selection_can_change() -> None:
    panel = StackedPanel([TextWidget("A"), TextWidget("B")])

    panel.select(1)

    assert panel.selected_index == 1


def test_grid_panel_accepts_cell_areas() -> None:
    panel = GridPanel(
        [TextWidget("A"), TextWidget("B")],
        columns="2fr 1fr",
        rows="1fr",
        gap=10,
        areas=[{"column": "1 / 2"}, {"column": "2 / 3"}],
    )

    assert panel.layout_kind == "grid"
    assert panel.columns == "2fr 1fr"
    assert panel.gap == "10px"
    assert panel.areas == [{"column": "1 / 2"}, {"column": "2 / 3"}]


def test_responsive_panel_tracks_breakpoint_and_directions() -> None:
    panel = ResponsivePanel(
        [TextWidget("A"), TextWidget("B")],
        breakpoint=640,
        wide_direction="left-to-right",
        narrow_direction="top-to-bottom",
    )

    assert panel.layout_kind == "responsive"
    assert panel.breakpoint == 640
    assert panel.wide_direction == "left-to-right"
    assert panel.narrow_direction == "top-to-bottom"


def test_action_widget_invokes_registered_callback() -> None:
    calls = []
    toolbar = Toolbar(
        [{"id": "reset", "label": "Reset"}],
        callbacks={"reset": lambda action_id: calls.append(action_id)},
    )

    toolbar._handle_frontend_event(toolbar, {"type": "activate", "id": "reset"}, None)

    assert calls == ["reset"]


def test_control_icon_metadata_is_synced() -> None:
    button = sx.Button(
        description="Help",
        icon="HelpCircle",
        icon_size="m",
    )

    assert button.icon == "HelpCircle"
    assert button.icon_size == "m"


def test_menubar_and_command_palette_store_actions() -> None:
    menu_actions = [
        {
            "label": "Chart",
            "items": [
                {"id": "new", "label": "New chart", "icon": "AddContent"},
            ],
        },
    ]
    palette_actions = [
        {
            "id": "fit",
            "label": "Fit chart",
            "category": "Chart",
            "icon": "FullScreen",
        },
    ]
    menu = MenuBar(menu_actions)
    palette = CommandPalette(palette_actions)

    assert menu.action_kind == "menubar"
    assert menu.actions == menu_actions
    assert palette.action_kind == "command_palette"
    assert palette.actions == palette_actions


def test_anylumino_controls_are_composable_children() -> None:
    button = sx.Button(description="Run")
    symbol = sx.TextInput(value="Greenhouse A", description="Dataset")
    interval = sx.Dropdown(
        options=["Daily", "Weekly"], value="Daily", description="Interval"
    )
    live = sx.Checkbox(value=True, description="Enabled")
    rows = sx.IntSlider(value=100, min=10, max=250, description="Rows")

    panel = GridPanel(
        {
            "button": button,
            "symbol": symbol,
            "interval": interval,
            "live": live,
            "rows": rows,
        },
        columns="1fr",
    )

    assert isinstance(button, sx.ControlWidget)
    assert panel.get_widget("button") is button
    assert panel["symbol"] is symbol
    assert panel.child_keys == ["button", "symbol", "interval", "live", "rows"]
    assert (
        panel.get_state(key=["widgets"])["widgets"][0] == f"anywidget:{button.model_id}"
    )


def test_date_controls_are_native_family_not_spectrum_controls() -> None:
    picker = DatePicker()

    assert picker.control_family == "native"
    assert isinstance(picker, sx.ControlWidget) is False


def test_widget_frontend_assets_are_lazy_paths() -> None:
    assert _asset_path(TabPanel._esm).parent.name == "layout"
    assert _asset_path(TextWidget._esm).parent.name == "layout"
    assert _asset_path(sx.ControlWidget._esm).name == "control_widget.bundle.js"
    assert _asset_path(sx.ControlWidget._esm).parent.name == "spectrum"
    assert _asset_path(sx.ControlWidget._css).name == "control_widget.css"
    assert _asset_path(DatePicker._esm).name == "native_control_widget.bundle.js"
    assert _asset_path(DatePicker._esm).parent.name == "spectrum"
    assert _asset_path(DatePicker._css).name == "native_control_widget.css"
    assert _asset_path(sx.SpectrumWidget._esm).name == "spectrum_widget.bundle.js"
    assert _asset_path(sx.SpectrumWidget._esm).parent.name == "spectrum"
    assert _asset_path(sx.SpectrumWidget._css).name == "spectrum_widget.css"
    assert _asset_path(ax.Widget._esm).name == "astryx_widget.bundle.js"
    assert _asset_path(ax.Widget._esm).parent.name == "astryx"
    assert _asset_path(ax.Widget._css).name == "astryx_widget.bundle.css"


def test_missing_static_asset_is_import_safe_until_loaded() -> None:
    asset = static_asset("__missing_anylumino_asset__.js")

    assert _asset_path(asset).name == "__missing_anylumino_asset__.js"
    with pytest.raises(FileNotFoundError, match="npm run build"):
        str(asset)


def test_datetime_picker_preserves_iso_precision() -> None:
    picker = DatetimePicker(value=datetime(2026, 6, 4, 12, 30, 15, 123456))

    assert picker.value == "2026-06-04T12:30:15.123456"


def test_dropdown_option_pairs_are_normalized_once() -> None:
    control = sx.Dropdown(options=[("One", 1), ("Two", 2)], index=1)

    assert control.options == (("One", 1), ("Two", 2))
    assert control.value == 2


def test_html_math_is_html_alias() -> None:
    widget = sx.HTMLMath(value="<strong>x</strong>", description="Value")

    assert widget.control_kind == "html"
    assert widget.html is True
    assert widget.value == "<strong>x</strong>"


def test_spectrum_component_wrappers_sync_kind_and_metadata() -> None:
    controls = {
        "search": sx.SearchInput(value="iris", description="Search"),
        "switch": sx.Switch(value=True, description="Enabled"),
        "status": sx.StatusLight(value=True, description="Ready", variant="positive"),
        "badge": sx.Badge(value="Ready", variant="informative", icon="InfoCircle"),
        "meter": sx.Meter(
            value=64, description="Coverage", variant="positive", readout=True
        ),
        "link": sx.Link("https://example.com", description="Docs"),
        "divider": sx.Divider(spectrum_size="l"),
    }

    assert controls["search"].control_kind == "search"
    assert controls["switch"].control_kind == "switch"
    assert controls["status"].variant == "positive"
    assert controls["badge"].icon == "InfoCircle"
    assert controls["meter"].readout is True
    assert controls["link"].href == "https://example.com"
    assert controls["divider"].spectrum_size == "l"


def test_spectrum_table_normalizes_mapping_rows_and_columns() -> None:
    table = sx.Table(
        rows=[
            {"symbol": "AAPL", "price": 195.12, "status": "Open"},
            {"symbol": "MSFT", "price": 423.85, "status": "Closed"},
        ],
        columns=[
            {"key": "symbol", "label": "Symbol", "sortable": True},
            {"key": "price", "label": "Price", "align": "end"},
            "status",
        ],
        row_key="symbol",
        selected=["AAPL"],
        selects="multiple",
        sortable=True,
        sort_key="price",
        sort_direction="desc",
        density="compact",
        quiet=True,
    )

    assert table.component_kind == "table"
    assert table.columns == [
        {"key": "symbol", "label": "Symbol", "sortable": True, "align": ""},
        {"key": "price", "label": "Price", "sortable": False, "align": "end"},
        {"key": "status", "label": "status", "sortable": False, "align": ""},
    ]
    assert table.rows == [
        {
            "value": "AAPL",
            "cells": {"symbol": "AAPL", "price": 195.12, "status": "Open"},
        },
        {
            "value": "MSFT",
            "cells": {"symbol": "MSFT", "price": 423.85, "status": "Closed"},
        },
    ]
    assert table.selected == ["AAPL"]
    assert table.selects == "multiple"
    assert table.sort_key == "price"
    assert table.sort_direction == "desc"
    assert table.density == "compact"
    assert table.quiet is True


def test_spectrum_table_normalizes_sequence_rows_without_columns() -> None:
    table = sx.Table(rows=[("Budget", "PDF"), ("Onboarding", "XLS")])

    assert table.columns == [
        {"key": "column_1", "label": "column_1", "sortable": False, "align": ""},
        {"key": "column_2", "label": "column_2", "sortable": False, "align": ""},
    ]
    assert table.rows == [
        {"value": "0", "cells": {"column_1": "Budget", "column_2": "PDF"}},
        {"value": "1", "cells": {"column_1": "Onboarding", "column_2": "XLS"}},
    ]


def test_spectrum_table_helpers_replace_append_update_and_remove_rows() -> None:
    table = sx.Table(
        rows=[{"order_id": "O-1", "symbol": "AAPL", "qty": 10, "status": "NEW"}],
        columns={
            "order_id": "Order",
            "symbol": "Symbol",
            "qty": "Qty",
            "status": "Status",
        },
        row_key="order_id",
        selected=["O-1"],
        selects="multiple",
    )

    table.append_row({"order_id": "O-2", "symbol": "MSFT", "qty": 5, "status": "NEW"})
    table.update_row("O-2", {"qty": 7, "status": "FILLED"})
    table.remove_row("O-1")

    assert table.columns == [
        {"key": "order_id", "label": "Order", "sortable": False, "align": ""},
        {"key": "symbol", "label": "Symbol", "sortable": False, "align": ""},
        {"key": "qty", "label": "Qty", "sortable": False, "align": ""},
        {"key": "status", "label": "Status", "sortable": False, "align": ""},
    ]
    assert table.rows == [
        {
            "value": "O-2",
            "cells": {
                "order_id": "O-2",
                "symbol": "MSFT",
                "qty": 7,
                "status": "FILLED",
            },
        },
    ]
    assert table.selected == []


def test_spectrum_table_prepend_row_inserts_before_existing_rows() -> None:
    table = sx.Table(
        rows=[{"order_id": "O-2", "symbol": "MSFT", "qty": 5, "status": "NEW"}],
        columns={
            "order_id": "Order",
            "symbol": "Symbol",
            "qty": "Qty",
            "status": "Status",
        },
        row_key="order_id",
    )

    assert (
        table.prepend_row(
            {"order_id": "O-1", "symbol": "AAPL", "qty": 10, "status": "NEW"}
        )
        == "O-1"
    )
    assert table.rows == [
        {
            "value": "O-1",
            "cells": {"order_id": "O-1", "symbol": "AAPL", "qty": 10, "status": "NEW"},
        },
        {
            "value": "O-2",
            "cells": {"order_id": "O-2", "symbol": "MSFT", "qty": 5, "status": "NEW"},
        },
    ]


def test_spectrum_table_set_rows_accepts_live_raw_rows() -> None:
    table = sx.Table(
        columns=["order_id", "status"], row_key="order_id", selected=["O-1", "O-3"]
    )

    table.set_rows(
        [
            {"order_id": "O-1", "status": "NEW"},
            {"order_id": "O-2", "status": "PARTIAL"},
        ],
    )

    assert table.rows == [
        {"value": "O-1", "cells": {"order_id": "O-1", "status": "NEW"}},
        {"value": "O-2", "cells": {"order_id": "O-2", "status": "PARTIAL"}},
    ]
    assert table.selected == ["O-1"]


def test_spectrum_table_append_row_skips_existing_auto_values_after_removal() -> None:
    table = sx.Table(
        rows=[("Budget", "PDF"), ("Onboarding", "XLS"), ("Quarterly", "DOC")]
    )

    table.remove_row("1")

    assert table.append_row(("Roadmap", "MD")) == "3"
    assert table.rows == [
        {"value": "0", "cells": {"column_1": "Budget", "column_2": "PDF"}},
        {"value": "2", "cells": {"column_1": "Quarterly", "column_2": "DOC"}},
        {"value": "3", "cells": {"column_1": "Roadmap", "column_2": "MD"}},
    ]


def test_spectrum_table_prepend_row_skips_existing_auto_values() -> None:
    table = sx.Table(rows=[("Budget", "PDF"), ("Onboarding", "XLS")])

    assert table.prepend_row(("Roadmap", "MD")) == "2"
    assert table.rows == [
        {"value": "2", "cells": {"column_1": "Roadmap", "column_2": "MD"}},
        {"value": "0", "cells": {"column_1": "Budget", "column_2": "PDF"}},
        {"value": "1", "cells": {"column_1": "Onboarding", "column_2": "XLS"}},
    ]


def test_spectrum_table_row_helpers_reject_duplicate_and_missing_rows() -> None:
    table = sx.Table(
        rows=[{"order_id": "O-1", "status": "NEW"}],
        columns=["order_id", "status"],
        row_key="order_id",
    )

    with pytest.raises(ValueError, match="table row already exists: O-1"):
        table.append_row({"order_id": "O-1", "status": "FILLED"})
    with pytest.raises(ValueError, match="table row already exists: O-1"):
        table.prepend_row({"order_id": "O-1", "status": "FILLED"})
    with pytest.raises(KeyError, match="table row not found: O-2"):
        table.update_row("O-2", {"status": "FILLED"})
    with pytest.raises(KeyError, match="table row not found: O-2"):
        table.remove_row("O-2")


def test_selection_range_slider_resolves_index_to_values() -> None:
    slider = sx.SelectionRangeSlider(
        options=["Mon", "Tue", "Wed", "Thu", "Fri"],
        index=(1, 3),
    )

    assert slider.value == ["Tue", "Thu"]
    assert slider.index == (1, 3)


def test_list_box_alias_uses_anylumino_select_control() -> None:
    control = sx.ListBox(options=["Greenhouse A", "Greenhouse B"], value="Greenhouse A")

    assert control.value == "Greenhouse A"
    assert control.options == ("Greenhouse A", "Greenhouse B")
    assert control.control_kind == "select"


def test_spectrum_widgets_share_generic_component_base() -> None:
    widgets = [
        sx.SpectrumElement("section"),
        sx.ClearButton(),
        sx.CloseButton(),
        sx.FieldGroup({"field": sx.TextInput(value="x")}),
        sx.Tooltip("More detail", {"trigger": sx.Button(description="Info")}),
        sx.OpacityCheckerboard(),
        sx.Table(rows=[{"name": "Budget", "type": "PDF"}]),
        sx.DialogBox({"body": TextWidget("Settings")}, title="Settings"),
        sx.Modal({"body": TextWidget("Confirm")}, title="Confirm"),
    ]

    assert [isinstance(widget, ComponentWidget) for widget in widgets] == [True] * len(
        widgets
    )
    assert [isinstance(widget, sx.SpectrumWidget) for widget in widgets] == [
        True
    ] * len(widgets)


def test_spectrum_widget_children_are_keyed_and_composable() -> None:
    text = sx.TextInput(value="Dataset")
    switch = sx.Switch(value=True, description="Enabled")
    group = sx.FieldGroup({"name": text, "enabled": switch}, orientation="vertical")

    assert group.component_kind == "field-group"
    assert group.child_keys == ["name", "enabled"]
    assert group["name"] is text
    assert group.get_owner("enabled") is switch
    assert group.orientation == "vertical"
    assert group.get_state(key=["widgets"])["widgets"] == [
        f"anywidget:{text.model_id}",
        f"anywidget:{switch.model_id}",
    ]


def test_spectrum_overlay_state_uses_is_open_without_shadowing_widget_open() -> None:
    dialog = sx.DialogBox({"body": TextWidget("Dialog")}, title="Settings", open=False)

    assert callable(dialog.open)
    assert dialog.is_open is False

    dialog.show()
    assert dialog.is_open is True

    dialog.hide()
    assert dialog.is_open is False

    dialog.toggle()
    assert dialog.is_open is True


def test_astryx_widgets_share_generic_component_base() -> None:
    widgets = [
        ax.Button("Run", variant="primary"),
        ax.TextInput(value="AAPL", label="Symbol", placeholder="Ticker"),
        ax.Component("Badge", label="Live", props={"variant": "success"}),
        ax.Stack({"button": ax.Button("Run")}, direction="horizontal", gap=1),
    ]

    assert [isinstance(widget, ComponentWidget) for widget in widgets] == [True] * len(
        widgets
    )
    assert [isinstance(widget, ax.Widget) for widget in widgets] == [True] * len(
        widgets
    )
    assert widgets[0].component_family == "astryx"
    assert widgets[0].component_name == "Button"
    assert widgets[0].label == "Run"
    assert widgets[0].variant == "primary"
    assert widgets[1].component_name == "TextInput"
    assert widgets[1].value == "AAPL"
    assert widgets[1].props == {"placeholder": "Ticker"}
    assert widgets[2].props == {"variant": "success"}


def test_astryx_useful_props_are_named_and_keep_the_escape_hatch() -> None:
    text = ax.Text(
        "P&L",
        text_type="supporting",
        color="secondary",
        weight="semibold",
        max_lines=1,
        data_attribute="kept",
    )
    params = signature(ax.Text).parameters

    assert [
        name for name in ("text_type", "color", "weight", "max_lines") if name in params
    ] == [
        "text_type",
        "color",
        "weight",
        "max_lines",
    ]
    assert "data-testid" not in params
    assert params["props"].kind.name == "VAR_KEYWORD"
    assert text.props == {
        "data_attribute": "kept",
        "type": "supporting",
        "color": "secondary",
        "weight": "semibold",
        "maxLines": 1,
    }


def test_astryx_classes_live_in_named_family_modules() -> None:
    assert ax.Widget.__module__ == "anylumino.astryx.base"
    assert ax.Text.__module__ == "anylumino.astryx.inputs"
    assert ax.Stack.__module__ == "anylumino.astryx.surfaces"
    assert ax.Table.__module__ == "anylumino.astryx.data"


def test_astryx_wrappers_do_not_swallow_shared_widget_arguments() -> None:
    brand = ax.Brand("desk", **{"color-accent": "#0057b8"})
    button = ax.Button("Run", color_mode="dark")
    heading = ax.Heading("Orders", brand=brand)
    card = ax.ClickableCard(label="Open", isDisabled=True)

    assert button.color_mode == "dark"
    assert "color_mode" not in button.props
    assert heading.brand == brand
    assert "brand" not in heading.props
    assert card.disabled is True


def test_astryx_component_rejects_unknown_names_and_preserves_data_props() -> None:
    component = ax.Component("List", props={"items": ["one"], "density": "compact"})

    assert component.props == {"items": ["one"], "density": "compact"}
    with pytest.raises(ValueError, match="unknown Astryx component 'Stak'"):
        ax.Component("Stak")


def test_astryx_open_state_and_action_payloads_are_synchronized() -> None:
    dialog = ax.Dialog(open=True)
    actions = []
    menu = ax.DropdownMenu(
        [{"label": "Export", "value": "export"}],
        label="Actions",
        action_callbacks=[lambda widget, action: actions.append((widget, action))],
    )

    assert dialog.is_open is True
    dialog.hide()
    assert dialog.is_open is False
    menu._handle_frontend_message(menu, {"type": "open", "is_open": False}, None)
    assert menu.is_open is False
    menu._handle_frontend_message(menu, {"type": "click", "value": "export"}, None)
    assert menu.last_action == "export"
    assert actions == [(menu, "export")]


def test_astryx_wrappers_cover_notebook_safe_component_families() -> None:
    rows = [
        {"id": "a", "symbol": "AAPL", "status": "Live"},
        {"id": "m", "symbol": "MSFT", "status": "Paused"},
    ]
    widgets = [
        ax.Text("Overview"),
        ax.Heading("Orders", level=3),
        ax.Badge("Live", variant="success"),
        ax.TextArea(value="Notes", label="Notes", rows=4),
        ax.NumberInput(value=25, label="Limit", min=0, max=100),
        ax.Slider(value=42, label="Risk", min=0, max=100),
        ax.ToggleButton(value=True, label="Pinned"),
        ax.Selector(
            [("Latency", "latency"), ("Volume", "volume")],
            value="latency",
            label="Metric",
        ),
        ax.MultiSelector(["Bid", "Ask", "Last"], value=["Bid", "Last"], label="Fields"),
        ax.TabList(["Summary", "Orders", "Fills"], value="Summary"),
        ax.SegmentedControl(["Compact", "Detailed"], value="Compact", label="Density"),
        ax.RadioList(["Auto", "Manual"], value="Auto", label="Mode"),
        ax.CheckboxList(["Quotes", "Trades"], value=["Quotes"], label="Streams"),
        ax.Table(rows, {"symbol": "Symbol", "status": "Status"}),
        ax.Card({"body": ax.Text("Card body")}),
        ax.AvatarGroup(["Ada", "Grace"], overflow_count=1),
        ax.FormLayout({"symbol": ax.TextInput(value="AAPL", label="Symbol")}),
        ax.Field(
            ax.TextInput(value="MSFT", label="Symbol", label_hidden=True),
            label="Field symbol",
        ),
        ax.InputGroup(
            ax.NumberInput(value=10, label="Qty", label_hidden=True),
            label="Quantity",
            suffix="sh",
        ),
        ax.Calendar("2026-07-09"),
        ax.FileInput(label="Upload", accept=".csv"),
        ax.StatusDot("Connected", variant="success"),
        ax.ProgressBar(55, label="Progress", variant="success"),
        ax.EmptyState(
            "No orders", description="The selected account has no open orders."
        ),
        ax.Banner("Market data connected", status="success"),
        ax.Code("symbol"),
        ax.CodeBlock("print('ready')", language="python"),
        ax.Outline([{"id": "summary", "label": "Summary", "level": 1}]),
        ax.TreeList(
            [
                {
                    "id": "src",
                    "label": "src",
                    "isExpanded": True,
                    "children": [{"id": "app", "label": "app.py"}],
                }
            ]
        ),
        ax.DropdownMenu(
            ["Refresh", {"label": "Export", "value": "export"}], label="Actions"
        ),
        ax.MoreMenu(["Edit", "Delete"]),
        ax.Tooltip("Run cell", ax.Button("Run")),
        ax.HoverCard(ax.Text("Preview"), ax.Button("Preview")),
        ax.Popover(ax.Text("Settings"), ax.Button("Open"), label="Settings"),
        ax.Typeahead(["AAPL", "MSFT"], value="AAPL", label="Symbol"),
        ax.Tokenizer(["Bid", "Ask", "Last"], value=["Bid", "Ask"], label="Fields"),
        ax.CommandPalette([{"id": "refresh", "label": "Refresh"}], value="refresh"),
        ax.Dialog(ax.Text("Inline dialog")),
        ax.AlertDialog("Confirm", "Continue?", action_label="Continue"),
    ]

    assert [isinstance(widget, ComponentWidget) for widget in widgets] == [True] * len(
        widgets
    )
    assert [isinstance(widget, ax.Widget) for widget in widgets] == [True] * len(
        widgets
    )
    assert widgets[1].component_name == "Heading"
    assert widgets[1].props == {"level": 3}
    assert widgets[3].component_name == "TextArea"
    assert widgets[7].props["options"] == [
        {"label": "Latency", "value": "latency"},
        {"label": "Volume", "value": "volume"},
    ]
    assert widgets[9].props["items"] == ["Summary", "Orders", "Fills"]
    assert widgets[13].props["rows"] == rows
    assert widgets[13].props["columns"] == [
        {
            "key": "symbol",
            "header": "Symbol",
            "width": {"kind": "proportional", "value": 1},
        },
        {
            "key": "status",
            "header": "Status",
            "width": {"kind": "proportional", "value": 1},
        },
    ]
    assert widgets[14].child_keys == ["body"]
    assert widgets[15].component_name == "AvatarGroup"
    assert widgets[16].component_name == "FormLayout"
    assert widgets[17].props["label"] == "Field symbol"
    assert widgets[18].props["suffix"] == "sh"
    assert widgets[19].component_name == "Calendar"
    assert widgets[20].component_name == "FileInput"
    assert widgets[29].props["items"][1]["value"] == "export"
    assert widgets[32].child_keys == ["trigger", "content"]
    assert widgets[33].child_keys == ["trigger", "content"]
    assert widgets[34].component_name == "Typeahead"
    assert widgets[34].props["items"][0] == {"id": "AAPL", "label": "AAPL"}
    assert widgets[35].value == ["Bid", "Ask"]
    assert widgets[36].component_name == "CommandPalette"
    assert widgets[37].props["isInline"] is True
    assert widgets[38].props["actionLabel"] == "Continue"


def test_astryx_lightbox_toggle_group_and_overlay_adapt_native_props() -> None:
    lightbox = ax.Lightbox(
        [
            {"src": "first.jpg", "alt": "First chart", "caption": "Daily view"},
            {"src": "clip.mp4", "alt": "Market replay", "type": "video"},
        ],
        open=True,
        index=1,
        zoom=True,
        auto_play=True,
    )
    toggle_group = ax.ToggleButtonGroup(
        [("Grid", "grid"), {"label": "List", "value": "list", "disabled": True}],
        value="grid",
        label="View mode",
        size="sm",
    )
    multiple_group = ax.ToggleButtonGroup(
        ["Bold", "Italic"],
        value="Bold",
        label="Formatting",
        selection_mode="multiple",
        orientation="vertical",
    )
    base = ax.Card(ax.Text("Preview"))
    action = ax.Button("Quick view")
    overlay = ax.Overlay(
        base,
        action,
        show_on="hover-or-focus",
        open=False,
        scrim="light",
        position="bottom",
        align="center",
    )

    assert lightbox.component_name == "Lightbox"
    assert lightbox.is_open is True
    assert lightbox.value == 1
    assert lightbox.props == {
        "media": [
            {"src": "first.jpg", "alt": "First chart", "caption": "Daily view"},
            {"src": "clip.mp4", "alt": "Market replay", "type": "video"},
        ],
        "isOpen": True,
        "hasZoom": True,
        "hasAutoPlay": True,
    }
    assert toggle_group.value == "grid"
    assert toggle_group.props == {
        "items": [
            {"label": "Grid", "value": "grid"},
            {"label": "List", "value": "list", "disabled": True},
        ],
        "type": "single",
        "orientation": "horizontal",
        "size": "sm",
    }
    assert multiple_group.value == ["Bold"]
    assert multiple_group.props["type"] == "multiple"
    assert overlay.child_keys == ["base", "content"]
    assert overlay["base"] is base
    assert overlay["content"] is action
    assert overlay.props == {
        "showOn": "hover-or-focus",
        "isOpen": False,
        "scrim": "light",
        "position": "bottom",
        "align": "center",
    }


def test_astryx_lightbox_and_toggle_group_reject_invalid_shapes() -> None:
    with pytest.raises(ValueError, match="at least one item"):
        ax.Lightbox([])
    with pytest.raises(ValueError, match="require 'src' and 'alt'"):
        ax.Lightbox({"src": "chart.jpg"})
    with pytest.raises(ValueError, match="must be 'image' or 'video'"):
        ax.Lightbox({"src": "chart.jpg", "alt": "Chart", "type": "audio"})
    with pytest.raises(ValueError, match="selection_mode"):
        ax.ToggleButtonGroup([], label="View", selection_mode="exclusive")
    with pytest.raises(TypeError, match="single-selection value"):
        ax.ToggleButtonGroup([], value=["grid"], label="View")


def test_astryx_theme_applies_reusable_brand_to_child_widgets() -> None:
    brand = ax.Brand(
        "desk",
        **{
            "color-accent": ("#0057b8", "#79b8ff"),
            "--color-text-primary": ("#111827", "#f9fafb"),
            "color-background-card": ("#ffffff", "#111111"),
            "radius-container": "8px",
        },
    )
    button = ax.Button("Run")
    panel = ax.Theme({"button": button}, brand=brand, mode="system", gap=3)

    assert brand == {
        "name": "desk",
        "tokens": {
            "--color-accent": ["#0057b8", "#79b8ff"],
            "--color-text-primary": ["#111827", "#f9fafb"],
            "--color-background-card": ["#ffffff", "#111111"],
            "--radius-container": "8px",
        },
    }
    assert panel.brand == brand
    assert panel.color_mode == "system"
    assert panel.props["gap"] == 3
    assert button.brand == brand
    assert button.color_mode == "system"


def test_astryx_built_theme_applies_precompiled_theme_descriptor_to_child_widgets(
    tmp_path: Path,
) -> None:
    css_path = tmp_path / "desk-theme.css"
    css_path.write_text(
        '[data-astryx-theme="desk-built"] { --color-accent: #0057b8; }',
        encoding="utf-8",
    )
    theme = ax.BuiltTheme(
        "desk-built",
        css=css_path,
        tokens={"color-accent": "#0057b8", "--radius-container": "6px"},
    )
    button = ax.Button("Run")
    panel = ax.Theme({"button": button}, brand=theme, mode="dark")

    assert theme == {
        "name": "desk-built",
        "built": True,
        "tokens": {"--color-accent": "#0057b8", "--radius-container": "6px"},
        "css": '[data-astryx-theme="desk-built"] { --color-accent: #0057b8; }',
        "components": {},
    }
    assert panel.brand == theme
    assert panel.color_mode == "dark"
    assert button.brand == theme
    assert button.color_mode == "dark"


@pytest.mark.parametrize("mode", ["light", "dark", "system"])
def test_astryx_theme_accepts_supported_modes_for_runtime_and_built_themes(
    mode: str,
) -> None:
    runtime = ax.Theme(
        brand=ax.Brand("runtime", **{"color-accent": ("#111111", "#eeeeee")}), mode=mode
    )
    built = ax.Theme(brand=ax.BuiltTheme("neutral"), mode=mode)

    assert runtime.color_mode == mode
    assert built.color_mode == mode
    assert built.brand == {
        "name": "neutral",
        "built": True,
        "tokens": {},
        "css": "",
        "components": {},
    }


def test_astryx_theme_rejects_invalid_theme_modes() -> None:
    with pytest.raises(ValueError, match="theme mode must be one of"):
        ax.Theme(color_mode="sepia")


def test_astryx_typeahead_can_use_python_backed_search(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    widget = ax.Typeahead(
        ["AAPL", "MSFT"],
        label="Symbol",
        search=lambda query: [{"id": f"{query}-1", "label": query.upper()}],
    )
    sent: list[dict[str, object]] = []
    monkeypatch.setattr(
        widget, "send", lambda content, buffers=None: sent.append(content)
    )

    widget._handle_frontend_message(
        widget,
        {"type": "search", "request_id": "req-1", "query": "nvda"},
        None,
    )

    assert widget.search_mode == "python"
    assert sent == [
        {
            "type": "search-results",
            "request_id": "req-1",
            "query": "nvda",
            "items": [{"id": "nvda-1", "label": "NVDA"}],
        },
    ]


def test_astryx_tokenizer_static_search_remains_default() -> None:
    widget = ax.Tokenizer(["Bid", "Ask"], value=["Bid"], label="Fields")

    assert widget.search_mode == "static"
    assert widget.props["items"] == [
        {"id": "Bid", "label": "Bid"},
        {"id": "Ask", "label": "Ask"},
    ]


def test_astryx_command_palette_can_use_python_backed_search(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    widget = ax.CommandPalette(
        [{"id": "refresh", "label": "Refresh"}],
        search=lambda query: [{"id": f"{query}-cmd", "label": f"Run {query}"}],
    )
    sent: list[dict[str, object]] = []
    monkeypatch.setattr(
        widget, "send", lambda content, buffers=None: sent.append(content)
    )

    widget._handle_frontend_message(
        widget,
        {"type": "search", "request_id": "cmd-1", "query": "rebalance"},
        None,
    )

    assert widget.search_mode == "python"
    assert sent == [
        {
            "type": "search-results",
            "request_id": "cmd-1",
            "query": "rebalance",
            "items": [{"id": "rebalance-cmd", "label": "Run rebalance"}],
        },
    ]


def test_astryx_table_normalizes_rows_and_supports_notebook_row_helpers() -> None:
    table = ax.Table(
        rows=[
            {"symbol": "AAPL", "price": 195.12, "venue": "XNAS", "status": "Open"},
            {"symbol": "MSFT", "price": 423.85, "venue": "XNAS", "status": "Open"},
        ],
        columns=[
            {"key": "symbol", "header": "Symbol", "sortable": True, "width": 1},
            {
                "key": "price",
                "header": "Price",
                "align": "end",
                "width": {"kind": "pixel", "value": 96},
            },
            ("Venue", "venue"),
            "status",
        ],
        row_key="symbol",
        selected=["AAPL"],
        selects="multiple",
        sortable=True,
        sort_key="price",
        sort_direction="desc",
        density="compact",
        dividers="grid",
        hover=True,
        width="720px",
    )

    assert table.width == "720px"
    assert table.row_key == "symbol"
    assert table.props["density"] == "compact"
    assert table.selected == ["AAPL"]
    assert table.selects == "multiple"
    assert table.sortable is True
    assert table.sort_key == "price"
    assert table.sort_direction == "desc"
    assert table.columns == [
        {
            "key": "symbol",
            "header": "Symbol",
            "sortable": True,
            "width": {"kind": "proportional", "value": 1},
        },
        {
            "key": "price",
            "header": "Price",
            "align": "end",
            "width": {"kind": "pixel", "value": 96},
        },
        {
            "key": "venue",
            "header": "Venue",
            "width": {"kind": "proportional", "value": 1},
        },
        {
            "key": "status",
            "header": "status",
            "width": {"kind": "proportional", "value": 1},
        },
    ]
    assert table.rows == [
        {"symbol": "AAPL", "price": 195.12, "venue": "XNAS", "status": "Open"},
        {"symbol": "MSFT", "price": 423.85, "venue": "XNAS", "status": "Open"},
    ]

    assert (
        table.append_row(
            {"symbol": "TSLA", "price": 187.42, "venue": "XNAS", "status": "Open"}
        )
        == "TSLA"
    )
    assert (
        table.prepend_row(
            {"symbol": "AMD", "price": 159.55, "venue": "XNAS", "status": "Open"}
        )
        == "AMD"
    )
    table.update_row("MSFT", {"price": 426.11, "status": "Filled"})
    table.remove_row("AAPL")

    assert [row["symbol"] for row in table.rows] == ["AMD", "MSFT", "TSLA"]
    assert table.selected == []
    assert table.rows[1]["price"] == 426.11
    assert table.rows[1]["status"] == "Filled"
    with pytest.raises(ValueError, match="table row already exists: MSFT"):
        table.append_row(
            {"symbol": "MSFT", "price": 1, "venue": "XNAS", "status": "Duplicate"}
        )
    with pytest.raises(KeyError, match="table row not found: AAPL"):
        table.remove_row("AAPL")


def test_astryx_table_selection_and_sort_callbacks_match_spectrum_table_api() -> None:
    table = ax.Table(
        rows=[
            {"symbol": "AAPL", "price": 195.12},
            {"symbol": "MSFT", "price": 423.85},
        ],
        columns=[
            {"key": "symbol", "header": "Symbol", "sortable": True},
            {"key": "price", "header": "Price", "sortable": True},
        ],
        row_key="symbol",
        selected=["AAPL"],
        selects="multiple",
        sortable=True,
    )
    selected_calls = []
    sort_calls = []

    table.on_select(lambda widget: selected_calls.append(widget.selected))
    table.on_sort(
        lambda widget: sort_calls.append((widget.sort_key, widget.sort_direction))
    )
    table.selected = ["AAPL", "MSFT"]
    table._handle_frontend_message(
        table, {"type": "selection", "selected": table.selected}, None
    )
    table.sort_key = "price"
    table.sort_direction = "asc"
    table._handle_frontend_message(
        table, {"type": "sort", "sort_key": "price", "sort_direction": "asc"}, None
    )

    assert selected_calls == [["AAPL", "MSFT"]]
    assert sort_calls == [("price", "asc")]


def test_astryx_table_accepts_sequence_rows_without_columns() -> None:
    table = ax.Table(rows=[("Budget", "PDF"), ("Onboarding", "XLS")], row_key=None)

    assert table.row_key == "__row_id"
    assert table.columns == [
        {
            "key": "column_1",
            "header": "column_1",
            "width": {"kind": "proportional", "value": 1},
        },
        {
            "key": "column_2",
            "header": "column_2",
            "width": {"kind": "proportional", "value": 1},
        },
    ]
    assert table.rows == [
        {"column_1": "Budget", "column_2": "PDF", "__row_id": "0"},
        {"column_1": "Onboarding", "column_2": "XLS", "__row_id": "1"},
    ]
    assert table.append_row(("Quarterly", "DOC")) == "2"


def test_astryx_widget_children_are_keyed_and_composable() -> None:
    button = ax.Button("Run")
    symbol = ax.TextInput(value="AAPL", label="Symbol")
    stack = ax.Stack(
        {"button": button, "symbol": symbol}, direction="horizontal", gap=2
    )

    assert stack.component_name == "Stack"
    assert stack.child_keys == ["button", "symbol"]
    assert stack["button"] is button
    assert stack.get_owner("symbol") is symbol
    assert stack.props == {"direction": "horizontal", "gap": 2}
    assert stack.get_state(key=["widgets"])["widgets"] == [
        f"anywidget:{button.model_id}",
        f"anywidget:{symbol.model_id}",
    ]


def test_single_widget_child_is_wrapped_instead_of_iterated() -> None:
    symbol = ax.TextInput(value="NVDA", label="Symbol")
    field = ax.Field(symbol, label="Wrapped symbol")
    quantity = ax.NumberInput(value=100, label="Quantity")
    group = ax.InputGroup(quantity, label="Quantity", suffix="sh")
    card = ax.Card({"body": ax.Text("Body")})
    theme = ax.Theme(card, brand=ax.Brand("desk", **{"color-accent": "#0057b8"}))

    assert field.child_keys == ["widget-1"]
    assert field.get_widget(0) is symbol
    assert group.child_keys == ["widget-1"]
    assert group.get_widget(0) is quantity
    assert theme.child_keys == ["widget-1"]
    assert theme.get_widget(0) is card
    assert card.brand == theme.brand


def test_keyed_children_widgets_reject_iteration() -> None:
    field = ax.Field(ax.TextInput(value="NVDA"), label="Wrapped symbol")
    panel = TabPanel({"first": TextWidget("First")})

    with pytest.raises(TypeError, match="Field is not iterable"):
        list(field)
    with pytest.raises(TypeError, match="TabPanel is not iterable"):
        list(panel)


def test_keyed_access_matches_across_layouts_and_components() -> None:
    first = TextWidget("First")
    second = TextWidget("Second")
    panel = TabPanel({"first": first, " second ": second})
    stack = ax.Stack({"first": ax.Text("First"), " second ": ax.Text("Second")})

    for keyed in (panel, stack):
        assert keyed.child_keys == ["first", "second"]
        assert 0 in keyed
        assert -2 in keyed
        assert 2 not in keyed
        assert "second" in keyed
        assert " second " in keyed
        assert "missing" not in keyed
        assert keyed[0] is keyed["first"]
        assert keyed.get_key(-1) == "second"
        assert keyed.get_index("second") == 1
        with pytest.raises(KeyError, match="unknown widget key 'missing'"):
            keyed["missing"]
        with pytest.raises(IndexError, match="widget index out of range: 5"):
            keyed[5]


def test_remove_widget_drops_per_child_metadata() -> None:
    split = SplitPanel(
        [TextWidget("One"), TextWidget("Two"), TextWidget("Three")],
        sizes=[1.0, 2.0, 3.0],
    )
    box = HBox([TextWidget("One"), TextWidget("Two")], stretches=[1, 5])
    grid = GridPanel(
        [TextWidget("One"), TextWidget("Two")],
        areas=[{"column": "1"}, {"column": "2"}],
    )

    split.remove_widget(1)
    box.remove_widget(0)
    grid.remove_widget(0)

    assert split.sizes == [1.0, 3.0]
    assert split.child_keys == ["widget-1", "widget-3"]
    assert box.stretches == [5]
    assert grid.areas == [{"column": "2"}]


def test_remove_widget_can_close_the_removed_child() -> None:
    kept = TextWidget("Kept")
    closed = TextWidget("Closed")
    panel = TabPanel({"kept": kept, "closed": closed})

    assert panel.remove_widget("closed", close=True) is closed
    assert closed.comm is None
    assert kept.comm is not None


def test_assigning_widgets_rekeys_and_readopts_children() -> None:
    first = TextWidget("First")
    second = TextWidget("Second")
    panel = TabPanel({"first": first, "second": second})

    added = TextWidget("Added")
    panel.widgets = [second, added]

    assert panel.child_keys == ["second", "widget-3"]
    assert panel.titles == ["second", ""]
    assert panel["second"] is second
    assert panel["widget-3"] is added


def test_assigning_astryx_widgets_propagates_the_brand() -> None:
    brand = ax.Brand("desk", **{"color-accent": "#0057b8"})
    theme = ax.Theme({"first": ax.Text("First")}, brand=brand, mode="dark")
    added = ax.Text("Added")

    theme.widgets = [*theme.widgets, added]

    assert theme.child_keys == ["first", "widget-2"]
    assert added.brand == brand
    assert added.color_mode == "dark"


def test_move_widget_keeps_keys_titles_and_selection_aligned() -> None:
    panel = TabPanel(
        {"alpha": TextWidget("A"), "beta": TextWidget("B"), "gamma": TextWidget("C")},
        selected_index=2,
    )
    gamma = panel["gamma"]

    panel._handle_frontend_message(panel, {"type": "move", "from": 0, "to": 2}, None)

    assert panel.child_keys == ["beta", "gamma", "alpha"]
    assert panel.titles == ["beta", "gamma", "alpha"]
    assert panel.selected_index == 1
    assert panel.selected_key == "gamma"
    assert panel["gamma"] is gamma


def test_activation_callbacks_share_one_registration_idiom() -> None:
    clicks: list[object] = []
    actions: list[object] = []
    toolbar = Toolbar([{"id": "reset", "label": "Reset"}])
    menu = ax.DropdownMenu([{"label": "Export", "value": "export"}], label="Actions")
    picker = DatePicker("2026-07-09")
    spectrum_button = sx.Button(description="Run")

    for widget in (toolbar, menu, picker, spectrum_button):
        widget.on_click(lambda source: clicks.append(source))
        widget.on_action(lambda source, value: actions.append((source, value)))

    toolbar._handle_frontend_event(toolbar, {"type": "activate", "id": "reset"}, None)
    menu._handle_frontend_message(menu, {"type": "click", "value": "export"}, None)
    picker.value = "2026-07-10"
    spectrum_button._handle_frontend_message(spectrum_button, {"type": "click"}, None)

    assert clicks == [toolbar, menu, picker, spectrum_button]
    assert actions == [(toolbar, "reset"), (menu, "export"), (picker, "2026-07-10")]


def test_activation_callbacks_can_be_unregistered() -> None:
    calls: list[str] = []

    def on_click(_widget: object) -> None:
        calls.append("click")

    def on_action(_widget: object, _value: object) -> None:
        calls.append("action")

    picker = DatePicker("2026-07-09", callbacks=[on_click])
    picker.on_action(on_action)
    picker.value = "2026-07-10"
    picker.on_click(on_click, remove=True)
    picker.on_action(on_action, remove=True)
    picker.value = "2026-07-11"

    assert calls == ["action", "click"]


def test_toolbar_callback_map_stays_mutable() -> None:
    calls: list[str] = []
    toolbar = Toolbar([{"id": "reset", "label": "Reset"}])

    toolbar.callbacks["reset"] = lambda action_id: calls.append(action_id)
    toolbar._handle_frontend_event(toolbar, {"type": "activate", "id": "reset"}, None)
    del toolbar.callbacks["reset"]
    toolbar._handle_frontend_event(toolbar, {"type": "activate", "id": "reset"}, None)

    assert calls == ["reset"]


def test_astryx_grid_columns_accept_ints_mappings_and_repeat_strings() -> None:
    fixed = ax.Grid(columns=3)
    mapped = ax.Grid(columns={"minWidth": 280, "repeat": "fit", "max": 4})
    translated = ax.Grid(columns="repeat(auto-fit, minmax(260px, 1fr))")
    filled = ax.Grid(columns="repeat(auto-fill, minmax(300px, 1fr))")

    assert fixed.props["columns"] == 3
    assert mapped.props["columns"] == {"minWidth": 280, "repeat": "fit", "max": 4}
    assert translated.props["columns"] == {"minWidth": 260, "repeat": "fit"}
    assert filled.props["columns"] == {"minWidth": 300, "repeat": "fill"}


def test_astryx_grid_rejects_css_columns_astryx_cannot_render() -> None:
    with pytest.raises(TypeError, match="'1fr 1fr' is not supported"):
        ax.Grid(columns="1fr 1fr")
    with pytest.raises(TypeError, match="must be an int, a mapping, or a repeat"):
        ax.Grid(columns=2.5)


def test_astryx_color_mode_supports_the_jupyterlab_theme() -> None:
    button = ax.Button("Run")
    theme = ax.Theme({"button": button}, mode="jupyterlab")

    assert theme.color_mode == "jupyterlab"
    assert button.color_mode == "jupyterlab"


def test_astryx_continuous_update_defers_input_values() -> None:
    live = ax.TextInput(value="AAPL", label="Symbol")
    deferred = ax.TextInput(value="AAPL", label="Symbol", continuous_update=False)
    slider = ax.Slider(value=42, label="Risk", continuous_update=False)

    assert live.continuous_update is True
    assert deferred.continuous_update is False
    assert slider.continuous_update is False
    assert "continuous_update" not in deferred.props
