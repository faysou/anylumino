import importlib
import re
from datetime import datetime
from inspect import signature
from pathlib import Path

import pytest
import traitlets as t

import anylumino
from anylumino import astryx as ax
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


@pytest.mark.parametrize("panel_type", [TabPanel, StackedPanel])
@pytest.mark.parametrize(
    "removed_key, selected_key",
    [("first", "second"), ("second", "third"), ("third", "second")],
)
def test_removing_a_child_preserves_selection(
    panel_type: type[LayoutWidget], removed_key: str, selected_key: str,
) -> None:
    children = {key: TextWidget(key) for key in ("first", "second", "third")}
    panel = panel_type(children)
    panel.select_key("second")

    removed = panel.remove_widget(removed_key)

    assert removed is children[removed_key]
    assert panel.selected_key == selected_key
    assert panel.selected_widget is children[selected_key]
    assert panel.selected_owner is children[selected_key]


@pytest.mark.parametrize("panel_type", [TabPanel, StackedPanel])
def test_replacing_children_preserves_selection_by_identity(panel_type: type[LayoutWidget]) -> None:
    children = {key: TextWidget(key) for key in ("first", "second", "third")}
    panel = panel_type(children)
    panel.select_key("second")

    panel.widgets = [children["third"], children["first"], children["second"]]

    assert panel.child_keys == ["third", "first", "second"]
    assert panel.selected_index == 2
    assert panel.selected_widget is children["second"]


@pytest.mark.parametrize("panel_type", [TabPanel, StackedPanel])
def test_replacing_children_clamps_selection(panel_type: type[LayoutWidget]) -> None:
    panel = panel_type({"first": TextWidget("First"), "second": TextWidget("Second")})
    panel.select_key("second")
    remaining = panel["first"]

    panel.widgets = [remaining]

    assert panel.child_keys == ["first"]
    assert panel.selected_index == 0
    assert panel.selected_widget is remaining


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


def test_date_controls_use_native_family() -> None:
    assert DatePicker().control_family == "native"


def test_widget_frontend_assets_are_lazy_paths() -> None:
    assert _asset_path(TabPanel._esm).parent.name == "layout"
    assert _asset_path(TextWidget._esm).parent.name == "layout"
    assert _asset_path(DatePicker._esm).name == "native_control_widget.bundle.js"
    assert _asset_path(DatePicker._esm).parent.name == "controls"
    assert _asset_path(DatePicker._css).name == "native_control_widget.css"
    assert _asset_path(ax.Widget._esm).name == "astryx_widget.bundle.js"
    assert _asset_path(ax.Widget._esm).parent.name == "astryx"
    assert _asset_path(ax.Widget._css).name == "astryx_widget.bundle.css"


def test_spectrum_namespace_is_removed() -> None:
    assert "spectrum" not in anylumino.__all__
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("anylumino.spectrum")


def test_missing_static_asset_is_import_safe_until_loaded() -> None:
    asset = static_asset("__missing_anylumino_asset__.js")

    assert _asset_path(asset).name == "__missing_anylumino_asset__.js"
    with pytest.raises(FileNotFoundError, match="npm run build"):
        str(asset)


def test_datetime_picker_preserves_iso_precision() -> None:
    picker = DatetimePicker(value=datetime(2026, 6, 4, 12, 30, 15, 123456))

    assert picker.value == "2026-06-04T12:30:15.123456"


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


def test_astryx_table_selection_and_sort_callbacks() -> None:
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


@pytest.mark.parametrize(
    "values", [{"id": "C", "qty": 7}, {"cells": {"id": "C", "qty": 7}}, ["C", 7]],
)
def test_astryx_table_row_identity_updates_preserve_selection(values) -> None:
    table = ax.Table(
        [{"id": "A", "qty": 1}, {"id": "B", "qty": 2}], row_key="id", selected=["B", "A"],
    )

    table.update_row("A", values)

    assert table.rows == [{"id": "C", "qty": 7}, {"id": "B", "qty": 2}]
    assert table.selected == ["B", "C"]


def test_astryx_table_duplicate_update_is_atomic() -> None:
    rows = [{"id": "A", "qty": 1}, {"id": "B", "qty": 2}]
    table = ax.Table(rows, row_key="id", selected=["A"])

    with pytest.raises(ValueError, match="table row already exists: B"):
        table.update_row("A", {"id": "B", "qty": 7})

    assert table.rows == rows
    assert table.selected == ["A"]


@pytest.mark.parametrize("ids", [("A", "A"), (1, "1")])
def test_astryx_table_rejects_duplicate_row_ids(ids) -> None:
    with pytest.raises(ValueError, match=f"table row already exists: {ids[1]}"):
        ax.Table([{"id": value} for value in ids], row_key="id")


def test_astryx_table_duplicate_replacement_is_atomic() -> None:
    rows = [{"id": "A", "qty": 1}, {"id": "B", "qty": 2}]
    table = ax.Table(rows, row_key="id", selected=["A"])

    with pytest.raises(ValueError, match="table row already exists: C"):
        table.set_rows([{"name": "C"}, {"name": "C"}], columns=["name"], row_key="name")

    assert table.rows == rows
    assert table.row_key == "id"
    assert table.selected == ["A"]


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
    button = ax.Button("Run")

    for widget in (toolbar, menu, picker, button):
        widget.on_click(lambda source: clicks.append(source))
        widget.on_action(lambda source, value: actions.append((source, value)))

    toolbar._handle_frontend_event(toolbar, {"type": "activate", "id": "reset"}, None)
    menu._handle_frontend_message(menu, {"type": "click", "value": "export"}, None)
    picker.value = "2026-07-10"
    button._handle_frontend_message(button, {"type": "click"}, None)

    assert clicks == [toolbar, menu, picker, button]
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


def test_every_frontend_message_type_has_a_python_handler() -> None:
    """Guard the cross-language message contract.

    A frontend ``model.send`` with no matching Python branch is traffic nobody
    reads, sent once per keystroke for input components. Adding a message type
    means wiring a handler and naming it here.
    """
    handled = {
        "activate",  # _ActionWidget._handle_frontend_event
        "click",  # ComponentWidget
        "close",  # ComponentWidget._handle_frontend_message
        "move",  # LayoutWidget._handle_frontend_message
        "open",  # ComponentWidget._handle_frontend_message
        "search",  # astryx Widget._handle_frontend_message
        "selection",  # astryx Table
        "sort",  # astryx Table
    }
    static_dir = Path(static_asset("astryx/astryx_widget.js")).parent.parent
    sources = [
        path
        for path in static_dir.rglob("*")
        if path.suffix in {".js", ".mjs"} and not path.name.endswith(".bundle.js")
    ]
    assert sources, "no frontend sources found"

    sent = set()
    for path in sources:
        text = path.read_text(encoding="utf-8")
        sent.update(re.findall(r"""\.send\(\{\s*type:\s*["'](\w[\w-]*)["']""", text))
        sent.update(re.findall(r"""message\.type\s*=\s*["'](\w[\w-]*)["']""", text))

    assert sent, "no frontend message types found"
    assert sent <= handled, f"unhandled frontend message types: {sorted(sent - handled)}"


def test_astryx_log_slider_drives_the_slider_in_exponent_space() -> None:
    slider = ax.LogSlider(100, label="Learning rate", base=10, min_exponent=-4, max_exponent=2)

    assert slider.component_name == "LogSlider"
    assert slider.value == 100
    assert slider.props == {
        "base": 10,
        "minExponent": -4,
        "maxExponent": 2,
        "step": 0.1,
    }


def test_astryx_selection_slider_normalizes_every_option_shape() -> None:
    scalars = ax.SelectionSlider(["XS", "S", "M"], label="Size", marks=True)
    pairs = ax.SelectionSlider([("Small", "s"), ("Large", "l")], label="Size")
    mapping = ax.SelectionSlider({"Low": 1, "High": 9}, label="Level")
    chosen = ax.SelectionSlider(["s", "m", "l"], value="m", label="Size")
    ranged = ax.SelectionSlider(["s", "m", "l"], value=["s", "l"], label="Range")

    assert scalars.component_name == "SelectionSlider"
    assert scalars.value == "XS"
    assert scalars.props["options"] == ["XS", "S", "M"]
    assert scalars.props["marks"] is True
    assert pairs.value == "s"
    assert pairs.props["options"] == [
        {"label": "Small", "value": "s"},
        {"label": "Large", "value": "l"},
    ]
    assert mapping.value == "1"
    assert chosen.value == "m"
    assert ranged.value == ["s", "l"]
    assert "marks" not in chosen.props


def test_astryx_option_sliders_accept_shared_widget_arguments() -> None:
    log = ax.LogSlider(10, label="Rate", continuous_update=False, width="240px")
    selection = ax.SelectionSlider(["a", "b"], label="Pick", disabled=True)

    assert log.continuous_update is False
    assert log.width == "240px"
    assert "continuous_update" not in log.props
    assert selection.disabled is True
    assert selection.continuous_update is True


@pytest.mark.parametrize(
    "widget_type, args, value",
    [(ax.Slider, (37,), 37), (ax.LogSlider, (100,), 100), (ax.SelectionSlider, (["small", "large"],), "small")],
)
@pytest.mark.parametrize("position", ["top", "left"])
def test_astryx_slider_label_positions(widget_type, args, value, position) -> None:
    default = widget_type(*args, label="Size", continuous_update=False)
    widget = widget_type(*args, label="Size", label_position=position, continuous_update=False)

    assert widget.value == value
    assert widget.label == "Size"
    assert widget.continuous_update is False
    assert "labelPosition" not in default.props
    assert widget.props == {**default.props, **({"labelPosition": "left"} if position == "left" else {})}


@pytest.mark.parametrize("widget_type, args", [(ax.Slider, ()), (ax.LogSlider, ()), (ax.SelectionSlider, (["small"],))])
def test_astryx_sliders_reject_invalid_label_positions(widget_type, args) -> None:
    with pytest.raises(ValueError, match="label_position must be 'top' or 'left'"):
        widget_type(*args, label_position="diagonal")


@pytest.mark.parametrize("widget_type, args", [(ax.Slider, ()), (ax.LogSlider, ()), (ax.SelectionSlider, (["small"],))])
@pytest.mark.parametrize("width, expected", [(80, "80px"), ("6rem", "6rem")])
def test_astryx_slider_label_widths(widget_type, args, width, expected) -> None:
    widget = widget_type(*args, label="Size", label_position="left", label_width=width)

    assert widget.props["labelPosition"] == "left"
    assert widget.props["labelWidth"] == expected
    assert widget.label == "Size"


@pytest.mark.parametrize(
    "widget_type, args, value",
    [(ax.TextInput, (), "Trade A"), (ax.Selector, (["Call", "Put"],), "Put"),
     (ax.MultiSelector, (["A", "B"],), ["B"])],
)
@pytest.mark.parametrize("position", ["top", "left"])
def test_astryx_input_label_layout_preserves_values(widget_type, args, value, position) -> None:
    widget = widget_type(*args, value=value, label="Trade", label_position=position, label_width=80)

    assert widget.value == value
    assert widget.label == "Trade"
    assert widget.props["labelWidth"] == "80px"
    assert widget.props.get("labelPosition", "top") == position


@pytest.mark.parametrize("widget_type, args", [(ax.TextInput, ()), (ax.Selector, ([],)), (ax.MultiSelector, ([],))])
def test_astryx_inputs_reject_invalid_label_positions(widget_type, args) -> None:
    with pytest.raises(ValueError, match="label_position must be 'top' or 'left'"):
        widget_type(*args, label_position="diagonal")


def test_astryx_pagination_syncs_the_page_and_reports_page_size_as_an_action() -> None:
    pages = ax.Pagination(3, total_items=120, page_size=20, page_size_options=[10, 20, 50])
    sizes: list[object] = []
    pages.on_action(lambda _widget, value: sizes.append(value))

    pages._handle_frontend_message(pages, {"type": "click", "value": 50}, None)

    assert pages.component_name == "Pagination"
    assert pages.value == 3
    assert pages.props == {
        "totalItems": 120,
        "pageSize": 20,
        "pageSizeOptions": [10, 20, 50],
    }
    assert sizes == [50]


def test_astryx_carousel_composes_children() -> None:
    carousel = ax.Carousel({"first": ax.Text("A"), "second": ax.Text("B")}, buttons=True, snap=True)

    assert carousel.component_name == "Carousel"
    assert carousel.child_keys == ["first", "second"]
    assert carousel.props == {"gap": 1, "hasButtons": True, "hasSnap": True}


def test_astryx_context_menu_dispatches_items_like_a_dropdown() -> None:
    chosen: list[object] = []
    target = ax.Text("Right-click me")
    menu = ax.ContextMenu(
        [("Copy", "copy"), ("Delete", "delete")],
        target,
        action_callbacks=[lambda _widget, value: chosen.append(value)],
    )

    menu._handle_frontend_message(menu, {"type": "click", "value": "delete"}, None)

    assert menu.component_name == "ContextMenu"
    assert menu.get_widget(0) is target
    assert menu.props["items"] == [
        {"label": "Copy", "value": "copy"},
        {"label": "Delete", "value": "delete"},
    ]
    assert menu.last_action == "delete"
    assert chosen == ["delete"]


def test_astryx_power_search_syncs_filters_as_the_value() -> None:
    config = {
        "name": "orders",
        "fields": [{"key": "symbol", "label": "Symbol", "operators": [{"key": "is", "label": "is"}]}],
    }
    search = ax.PowerSearch(
        config,
        filters=[{"field": "symbol", "operator": "is", "value": "AAPL"}],
        label="Filter",
        clear=True,
    )

    assert search.component_name == "PowerSearch"
    assert search.value == [{"field": "symbol", "operator": "is", "value": "AAPL"}]
    assert search.props["config"] == config
    assert search.props["hasClear"] is True
    assert search.label == "Filter"


def test_record_components_take_items_and_expose_the_items_accessor() -> None:
    selector = ax.Selector(["call", "put"], value="call", label="Select")
    assert selector.props["options"] == ["call", "put"]
    assert selector.items == ["call", "put"]

    checkbox_list = ax.CheckboxList(["a", "b"], value=["a"], label="Streams")
    assert checkbox_list.props["items"] == ["a", "b"]
    assert checkbox_list.items == ["a", "b"]

    multi = ax.MultiSelector(["x", "y"], value=["x"], label="Fields")
    assert multi.props["options"] == ["x", "y"]

    slider = ax.SelectionSlider(["s", "m", "l"], value="m", label="Size")
    assert slider.props["options"] == ["s", "m", "l"]

    selector.items = {"Call option": "call2", "Put option": "put2"}
    assert selector.props["options"] == [
        {"label": "Call option", "value": "call2"},
        {"label": "Put option", "value": "put2"},
    ]
    checkbox_list.items = ["a", "b", "c"]
    assert checkbox_list.props["items"] == ["a", "b", "c"]
    assert "options" not in checkbox_list.props


def test_inputs_map_select_on_focus_to_the_frontend_prop() -> None:
    plain_text = ax.TextInput(value="AAPL", label="Symbol")
    assert "selectOnFocus" not in plain_text.props

    selecting_text = ax.TextInput(value="AAPL", label="Symbol", select_on_focus=True)
    assert selecting_text.props["selectOnFocus"] is True

    default_number = ax.NumberInput(10, label="Qty")
    assert "selectOnFocus" not in default_number.props

    opted_out = ax.NumberInput(10, label="Qty", select_on_focus=False)
    assert opted_out.props["selectOnFocus"] is False


def test_astryx_layout_panels_live_in_the_layout_module() -> None:
    assert ax.TabPanel.__module__ == "anylumino.astryx.layout"
    assert ax.SplitPanel.__module__ == "anylumino.astryx.layout"
    assert [panel.component_name for panel in (
        ax.TabPanel(),
        ax.StackedPanel(),
        ax.AccordionPanel(),
        ax.ScrollBox(),
        ax.SplitPanel(),
        ax.ResponsivePanel(),
    )] == ["TabPanel", "StackedPanel", "AccordionPanel", "ScrollBox", "SplitPanel", "ResponsivePanel"]


def test_astryx_tab_panel_keys_titles_and_selection_match_the_lumino_api() -> None:
    orders = ax.Text("Orders")
    fills = ax.Text("Fills")
    logs = ax.Text("Logs")
    tabs = ax.TabPanel({"orders": orders, "fills": fills}, titles={"fills": "Fills today"}, size="sm", divider=False)

    assert tabs.child_keys == ["orders", "fills"]
    assert tabs.titles == ["orders", "Fills today"]
    assert tabs.props == {"size": "sm", "hasDivider": False, "gap": 2}
    assert tabs.selected_index == 0
    assert tabs.selected_key == "orders"

    tabs.select_key("fills")
    assert tabs.selected_index == 1
    assert tabs.selected_widget is fills

    tabs.add_tab(logs, "Log lines", key="logs", select=True)
    assert tabs.child_keys == ["orders", "fills", "logs"]
    assert tabs.titles == ["orders", "Fills today", "Log lines"]
    assert tabs.selected_key == "logs"

    tabs.remove_widget("fills")
    assert tabs.child_keys == ["orders", "logs"]
    assert tabs.selected_key == "logs"


def test_astryx_stacked_panel_selection_can_change() -> None:
    stacked = ax.StackedPanel([ax.Text("A"), ax.Text("B")], keys=["a", "b"], selected_index=1)

    assert stacked.selected_key == "b"
    stacked.select(0)
    assert stacked.selected_key == "a"
    stacked.select_key("b")
    assert stacked.selected_index == 1


def test_astryx_accordion_panel_tracks_open_sections_in_value() -> None:
    single = ax.AccordionPanel({"first": ax.Text("1"), "second": ax.Text("2")})
    assert single.props == {"type": "single", "hasDividers": True}
    assert single.value == "first"
    assert single.open_keys == ["first"]

    single.open_key("second")
    assert single.value == "second"
    single.close_key("second")
    assert single.value == ""
    assert single.open_keys == []

    multiple = ax.AccordionPanel(
        {"first": ax.Text("1"), "second": ax.Text("2"), "third": ax.Text("3")},
        open=["third", 0],
        multiple=True,
        dividers=False,
    )
    assert multiple.props == {"type": "multiple", "hasDividers": False}
    assert multiple.value == ["third", "first"]

    multiple.open_key("second")
    assert multiple.value == ["third", "first", "second"]
    multiple.close_key(0)
    assert multiple.value == ["third", "second"]

    with pytest.raises(ValueError, match="single section"):
        ax.AccordionPanel({"first": ax.Text("1"), "second": ax.Text("2")}, open=["first", "second"])


def test_astryx_scroll_box_forwards_viewport_options() -> None:
    scroll = ax.ScrollBox([ax.Text("Line")], axis="both", label="Log lines", height=240, max_width=600, padding=2)

    assert scroll.label == "Log lines"
    assert scroll.height == "240px"
    assert scroll.props == {"axis": "both", "gap": 2, "padding": 2, "height": 240, "maxWidth": 600}
    with pytest.raises(ValueError, match="axis must be one of"):
        ax.ScrollBox([ax.Text("Line")], axis="diagonal")


def test_astryx_split_panel_tracks_orientation_and_sizes() -> None:
    left = ax.Text("Left")
    right = ax.Text("Right")
    split = ax.SplitPanel({"left": left, "right": right}, orientation="vertical", sizes=[0.3, 0.7], min_size=120)

    assert split.props == {"orientation": "vertical", "minSize": 120}
    assert split.sizes == [0.3, 0.7]
    assert split.width == "100%"
    assert split.height == "420px"

    split.remove_widget("left")
    assert split.sizes == [0.7]
    assert split.child_keys == ["right"]
    with pytest.raises(ValueError, match="orientation must be one of"):
        ax.SplitPanel([left], orientation="diagonal")


def test_astryx_responsive_panel_forwards_breakpoint_and_directions() -> None:
    panel = ax.ResponsivePanel([ax.Text("A"), ax.Text("B")], breakpoint=500, wide_direction="vertical", narrow_direction="horizontal", gap=4)

    assert panel.props == {
        "breakpoint": 500,
        "wideDirection": "vertical",
        "narrowDirection": "horizontal",
        "gap": 4,
    }
    with pytest.raises(ValueError, match="narrow_direction must be one of"):
        ax.ResponsivePanel([ax.Text("A")], narrow_direction="diagonal")
