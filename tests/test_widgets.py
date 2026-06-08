from datetime import datetime
from pathlib import Path

import pytest
import traitlets as t

from anylumino import (
    AccordionPanel,
    Badge,
    BoxPanel,
    Button,
    Checkbox,
    ClearButton,
    CloseButton,
    CommandPalette,
    ComponentWidget,
    ControlWidget,
    DatePicker,
    DatetimePicker,
    DialogBox,
    Divider,
    Dropdown,
    FieldGroup,
    GridPanel,
    HBox,
    HTMLMath,
    IntSlider,
    Link,
    ListBox,
    Meter,
    Modal,
    OpacityCheckerboard,
    DockPanel,
    LayoutWidget,
    MenuBar,
    ResponsivePanel,
    ScrollBox,
    SearchInput,
    SelectionRangeSlider,
    SpectrumElement,
    SpectrumWidget,
    SplitPanel,
    StackedPanel,
    TabPanel,
    TextInput,
    TextWidget,
    Tooltip,
    Toolbar,
    StatusLight,
    Switch,
    Table,
    VBox,
)
from anylumino._common import static_asset


def _asset_path(asset: object) -> Path:
    path = getattr(asset, "_path", None)
    assert isinstance(path, Path)
    return path


def test_tab_panel_serializes_child_widgets_as_anywidget_refs() -> None:
    first = TextWidget("First")
    second = TextWidget("Second")

    panel = TabPanel([first, second], titles=["One", "Two"], selected_index=1)

    assert panel.get_state(key=["widgets", "child_keys", "titles", "selected_index"]) == {
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
    button = Button(
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
    button = Button(description="Run")
    symbol = TextInput(value="Greenhouse A", description="Dataset")
    interval = Dropdown(options=["Daily", "Weekly"], value="Daily", description="Interval")
    live = Checkbox(value=True, description="Enabled")
    rows = IntSlider(value=100, min=10, max=250, description="Rows")

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

    assert isinstance(button, ControlWidget)
    assert panel.get_widget("button") is button
    assert panel["symbol"] is symbol
    assert panel.child_keys == ["button", "symbol", "interval", "live", "rows"]
    assert panel.get_state(key=["widgets"])["widgets"][0] == f"anywidget:{button.model_id}"


def test_date_controls_are_native_family_not_spectrum_controls() -> None:
    picker = DatePicker()

    assert picker.control_family == "native"
    assert isinstance(picker, ControlWidget) is False


def test_widget_frontend_assets_are_lazy_paths() -> None:
    assert _asset_path(ControlWidget._esm).name == "control_widget.bundle.js"
    assert _asset_path(ControlWidget._css).name == "control_widget.css"
    assert _asset_path(DatePicker._esm).name == "native_control_widget.bundle.js"
    assert _asset_path(DatePicker._css).name == "native_control_widget.css"
    assert _asset_path(SpectrumWidget._esm).name == "spectrum_widget.bundle.js"
    assert _asset_path(SpectrumWidget._css).name == "spectrum_widget.css"


def test_missing_static_asset_is_import_safe_until_loaded() -> None:
    asset = static_asset("__missing_anylumino_asset__.js")

    assert _asset_path(asset).name == "__missing_anylumino_asset__.js"
    with pytest.raises(FileNotFoundError, match="npm run build"):
        str(asset)


def test_datetime_picker_preserves_iso_precision() -> None:
    picker = DatetimePicker(value=datetime(2026, 6, 4, 12, 30, 15, 123456))

    assert picker.value == "2026-06-04T12:30:15.123456"


def test_dropdown_option_pairs_are_normalized_once() -> None:
    control = Dropdown(options=[("One", 1), ("Two", 2)], index=1)

    assert control.options == (("One", 1), ("Two", 2))
    assert control.value == 2


def test_html_math_is_html_alias() -> None:
    widget = HTMLMath(value="<strong>x</strong>", description="Value")

    assert widget.control_kind == "html"
    assert widget.html is True
    assert widget.value == "<strong>x</strong>"


def test_spectrum_component_wrappers_sync_kind_and_metadata() -> None:
    controls = {
        "search": SearchInput(value="iris", description="Search"),
        "switch": Switch(value=True, description="Enabled"),
        "status": StatusLight(value=True, description="Ready", variant="positive"),
        "badge": Badge(value="Ready", variant="informative", icon="InfoCircle"),
        "meter": Meter(value=64, description="Coverage", variant="positive", readout=True),
        "link": Link("https://example.com", description="Docs"),
        "divider": Divider(spectrum_size="l"),
    }

    assert controls["search"].control_kind == "search"
    assert controls["switch"].control_kind == "switch"
    assert controls["status"].variant == "positive"
    assert controls["badge"].icon == "InfoCircle"
    assert controls["meter"].readout is True
    assert controls["link"].href == "https://example.com"
    assert controls["divider"].spectrum_size == "l"


def test_spectrum_table_normalizes_mapping_rows_and_columns() -> None:
    table = Table(
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
        {"value": "AAPL", "cells": {"symbol": "AAPL", "price": 195.12, "status": "Open"}},
        {"value": "MSFT", "cells": {"symbol": "MSFT", "price": 423.85, "status": "Closed"}},
    ]
    assert table.selected == ["AAPL"]
    assert table.selects == "multiple"
    assert table.sort_key == "price"
    assert table.sort_direction == "desc"
    assert table.density == "compact"
    assert table.quiet is True


def test_spectrum_table_normalizes_sequence_rows_without_columns() -> None:
    table = Table(rows=[("Budget", "PDF"), ("Onboarding", "XLS")])

    assert table.columns == [
        {"key": "column_1", "label": "column_1", "sortable": False, "align": ""},
        {"key": "column_2", "label": "column_2", "sortable": False, "align": ""},
    ]
    assert table.rows == [
        {"value": "0", "cells": {"column_1": "Budget", "column_2": "PDF"}},
        {"value": "1", "cells": {"column_1": "Onboarding", "column_2": "XLS"}},
    ]


def test_spectrum_table_helpers_replace_append_update_and_remove_rows() -> None:
    table = Table(
        rows=[{"order_id": "O-1", "symbol": "AAPL", "qty": 10, "status": "NEW"}],
        columns={"order_id": "Order", "symbol": "Symbol", "qty": "Qty", "status": "Status"},
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
            "cells": {"order_id": "O-2", "symbol": "MSFT", "qty": 7, "status": "FILLED"},
        },
    ]
    assert table.selected == []


def test_spectrum_table_prepend_row_inserts_before_existing_rows() -> None:
    table = Table(
        rows=[{"order_id": "O-2", "symbol": "MSFT", "qty": 5, "status": "NEW"}],
        columns={"order_id": "Order", "symbol": "Symbol", "qty": "Qty", "status": "Status"},
        row_key="order_id",
    )

    assert table.prepend_row({"order_id": "O-1", "symbol": "AAPL", "qty": 10, "status": "NEW"}) == "O-1"
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
    table = Table(columns=["order_id", "status"], row_key="order_id", selected=["O-1", "O-3"])

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
    table = Table(rows=[("Budget", "PDF"), ("Onboarding", "XLS"), ("Quarterly", "DOC")])

    table.remove_row("1")

    assert table.append_row(("Roadmap", "MD")) == "3"
    assert table.rows == [
        {"value": "0", "cells": {"column_1": "Budget", "column_2": "PDF"}},
        {"value": "2", "cells": {"column_1": "Quarterly", "column_2": "DOC"}},
        {"value": "3", "cells": {"column_1": "Roadmap", "column_2": "MD"}},
    ]


def test_spectrum_table_prepend_row_skips_existing_auto_values() -> None:
    table = Table(rows=[("Budget", "PDF"), ("Onboarding", "XLS")])

    assert table.prepend_row(("Roadmap", "MD")) == "2"
    assert table.rows == [
        {"value": "2", "cells": {"column_1": "Roadmap", "column_2": "MD"}},
        {"value": "0", "cells": {"column_1": "Budget", "column_2": "PDF"}},
        {"value": "1", "cells": {"column_1": "Onboarding", "column_2": "XLS"}},
    ]


def test_spectrum_table_row_helpers_reject_duplicate_and_missing_rows() -> None:
    table = Table(
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
    slider = SelectionRangeSlider(
        options=["Mon", "Tue", "Wed", "Thu", "Fri"],
        index=(1, 3),
    )

    assert slider.value == ["Tue", "Thu"]
    assert slider.index == (1, 3)


def test_list_box_alias_uses_anylumino_select_control() -> None:
    control = ListBox(options=["Greenhouse A", "Greenhouse B"], value="Greenhouse A")

    assert control.value == "Greenhouse A"
    assert control.options == ("Greenhouse A", "Greenhouse B")
    assert control.control_kind == "select"


def test_spectrum_widgets_share_generic_component_base() -> None:
    widgets = [
        SpectrumElement("section"),
        ClearButton(),
        CloseButton(),
        FieldGroup({"field": TextInput(value="x")}),
        Tooltip("More detail", {"trigger": Button(description="Info")}),
        OpacityCheckerboard(),
        Table(rows=[{"name": "Budget", "type": "PDF"}]),
        DialogBox({"body": TextWidget("Settings")}, title="Settings"),
        Modal({"body": TextWidget("Confirm")}, title="Confirm"),
    ]

    assert [isinstance(widget, ComponentWidget) for widget in widgets] == [True] * len(widgets)
    assert [isinstance(widget, SpectrumWidget) for widget in widgets] == [True] * len(widgets)


def test_spectrum_widget_children_are_keyed_and_composable() -> None:
    text = TextInput(value="Dataset")
    switch = Switch(value=True, description="Enabled")
    group = FieldGroup({"name": text, "enabled": switch}, orientation="vertical")

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
    dialog = DialogBox({"body": TextWidget("Dialog")}, title="Settings", open=False)

    assert callable(dialog.open)
    assert dialog.is_open is False

    dialog.show()
    assert dialog.is_open is True

    dialog.hide()
    assert dialog.is_open is False

    dialog.toggle()
    assert dialog.is_open is True
