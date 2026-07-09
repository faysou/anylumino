from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any

import traitlets as t

from .common import json_value as _json_value
from .common import static_asset
from .components import ComponentWidget
from .layout import ChildInput


def _clean_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _clean_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean_value(item) for item in value]
    return _json_value(value)


def _clean_props(props: Mapping[str, Any] | None) -> dict[str, Any]:
    return {str(key): _clean_value(value) for key, value in dict(props or {}).items()}


def _option_records(options: Iterable[Any] | Mapping[str, Any]) -> list[Any]:
    if isinstance(options, Mapping):
        return [{"label": str(label), "value": str(value)} for label, value in options.items()]

    normalized = []
    for option in options:
        if isinstance(option, Mapping):
            normalized.append(_clean_value(option))
        elif isinstance(option, (list, tuple)) and len(option) == 2:
            label, value = option
            normalized.append({"label": str(label), "value": str(value)})
        else:
            normalized.append(_clean_value(option))
    return normalized


def _table_column_key(index: int) -> str:
    return f"column_{index + 1}"


def _astryx_table_width(value: Any) -> Any:
    if value is None:
        return {"kind": "proportional", "value": 1}
    if isinstance(value, (int, float)):
        return {"kind": "proportional", "value": value}
    return _clean_value(value)


def _table_columns(columns: Iterable[Any] | Mapping[str, Any] | None, rows: Iterable[Any]) -> list[Any]:
    row_list = list(rows)
    if columns is None:
        first = row_list[0] if row_list else {}
        if isinstance(first, Mapping):
            columns = list(first.keys())
        elif isinstance(first, (list, tuple)):
            columns = [_table_column_key(index) for index in range(len(first))]
        else:
            columns = ["value"]
    if isinstance(columns, Mapping):
        return [{"key": str(key), "header": str(header), "width": {"kind": "proportional", "value": 1}} for key, header in columns.items()]

    normalized = []
    for index, column in enumerate(columns):
        if isinstance(column, Mapping):
            item = _clean_value(column)
            item["key"] = str(item.get("key", item.get("value", _table_column_key(index))))
            item["header"] = str(item.get("header", item.get("label", item["key"])))
            if "width" not in item:
                item["width"] = {"kind": "proportional", "value": 1}
            else:
                item["width"] = _astryx_table_width(item["width"])
            normalized.append(item)
        elif isinstance(column, (list, tuple)) and len(column) == 2:
            header, key = column
            normalized.append({"key": str(key), "header": str(header), "width": {"kind": "proportional", "value": 1}})
        else:
            normalized.append({"key": str(column), "header": str(column), "width": {"kind": "proportional", "value": 1}})
    return normalized


def _table_rows(rows: Iterable[Any], columns: list[dict[str, Any]], row_key: str) -> list[dict[str, Any]]:
    normalized = []
    for index, row in enumerate(rows):
        if isinstance(row, Mapping):
            item = {column["key"]: _clean_value(row.get(column["key"], "")) for column in columns}
            item[row_key] = _clean_value(row.get(row_key, index))
        elif isinstance(row, (list, tuple)):
            item = {
                column["key"]: _clean_value(row[column_index]) if column_index < len(row) else ""
                for column_index, column in enumerate(columns)
            }
            item[row_key] = str(index)
        else:
            item = {columns[0]["key"]: _clean_value(row)} if columns else {"value": _clean_value(row)}
            item[row_key] = str(index)
        normalized.append(item)
    return normalized


class AstryxWidget(ComponentWidget):
    """Base widget for Astryx-backed components.

    This class owns the shared trait synchronization used by all Astryx
    wrappers. Most users should instantiate a concrete wrapper such as
    :class:`AstryxButton`, :class:`AstryxStack`, or :class:`AstryxTable`
    instead of this base class.
    """

    _esm = static_asset("astryx/astryx_widget.bundle.js")
    _css = static_asset("astryx/astryx_widget.bundle.css")

    component_family = t.Unicode("astryx").tag(sync=True)
    component_name = t.Unicode("Stack").tag(sync=True)
    props = t.Dict(default_value={}).tag(sync=True)
    color_mode = t.Unicode("light").tag(sync=True)
    theme = t.Unicode("neutral").tag(sync=True)

    def __init__(
        self,
        component_name: str = "Stack",
        children: ChildInput = None,
        *,
        props: Mapping[str, Any] | None = None,
        text: str = "",
        label: str = "",
        value: Any = None,
        disabled: bool = False,
        variant: str = "",
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            children,
            component_kind=component_name,
            component_name=component_name,
            props=_clean_props(props),
            text=text,
            label=label,
            value=_clean_value(value),
            disabled=disabled,
            variant=variant,
            callbacks=callbacks,
            **kwargs,
        )


class AstryxComponent(AstryxWidget):
    """Generic wrapper for an Astryx React component.

    Use this escape hatch for supported Astryx components that do not yet have
    a dedicated Python wrapper. ``component_name`` must match the frontend
    component registry, while ``props`` is serialized directly to React props.
    """

    def __init__(
        self,
        component_name: str,
        children: ChildInput = None,
        *,
        props: Mapping[str, Any] | None = None,
        text: str = "",
        label: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            component_name,
            children,
            props=props,
            text=text,
            label=label,
            **kwargs,
        )


class AstryxText(AstryxWidget):
    """Render themed Astryx body text.

    Pass plain text as the first argument. Astryx text styling props such as
    ``type``, ``color``, ``weight``, ``maxLines``, and ``display`` can be passed
    as keyword arguments or in ``props``.
    """

    def __init__(self, text: str, *, props: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__("Text", text=text, props=props, **kwargs)


class AstryxHeading(AstryxWidget):
    """Render a semantic Astryx heading.

    ``level`` controls the HTML heading level from 1 through 6. Use this for
    section titles and table/card headers instead of trying to make
    :class:`AstryxText` act as a heading.
    """

    def __init__(self, text: str, *, level: int = 3, props: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        if not 1 <= level <= 6:
            raise ValueError("heading level must be between 1 and 6")
        super().__init__("Heading", text=text, props={"level": level, **dict(props or {}), **kwargs})


class AstryxBadge(AstryxWidget):
    """Render a compact status or category badge.

    ``label`` is the visible badge text and ``variant`` selects the Astryx
    visual treatment, for example ``"neutral"``, ``"success"``, or ``"info"``.
    """

    def __init__(self, label: str, *, variant: str = "neutral", **props: Any) -> None:
        super().__init__("Badge", label=label, variant=variant, props=props)


class AstryxButton(AstryxWidget):
    """Render an Astryx push button.

    Use ``callbacks`` for Python-side click handlers. Additional keyword
    arguments are forwarded as Astryx button props, while ``disabled`` maps to
    the frontend disabled state.
    """

    def __init__(
        self,
        label: str,
        *,
        variant: str = "secondary",
        disabled: bool = False,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        **props: Any,
    ) -> None:
        super().__init__("Button", label=label, variant=variant, disabled=disabled, callbacks=callbacks, props=props)


class AstryxIconButton(AstryxWidget):
    """Render an icon-only Astryx button with an accessible label.

    ``label`` describes the action for assistive technology and tooltips.
    ``icon`` names the Astryx icon to show inside the button.
    """

    def __init__(
        self,
        label: str,
        *,
        icon: str = "close",
        variant: str = "secondary",
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "IconButton",
            label=label,
            icon=icon,
            variant=variant,
            callbacks=callbacks,
            props={**props, "icon": icon},
        )


class AstryxToggleButton(AstryxWidget):
    """Render a two-state Astryx toggle button.

    The boolean ``value`` trait is synchronized with the frontend selected
    state. Use this for compact on/off actions that should look like buttons.
    """

    def __init__(self, value: bool = False, *, label: str, disabled: bool = False, **props: Any) -> None:
        super().__init__("ToggleButton", label=label, value=value, disabled=disabled, props=props)


class AstryxTextInput(AstryxWidget):
    """Render a single-line Astryx text input.

    ``value`` is synchronized with the frontend input value. Pass ``label`` for
    accessibility and ``placeholder`` for empty-field hint text.
    """

    def __init__(
        self,
        value: str = "",
        *,
        label: str = "",
        placeholder: str = "",
        disabled: bool = False,
        **props: Any,
    ) -> None:
        super().__init__(
            "TextInput",
            label=label,
            value=value,
            disabled=disabled,
            props={"placeholder": placeholder, **props},
        )


class AstryxTextArea(AstryxWidget):
    """Render a multiline Astryx text area.

    ``rows`` controls the visible text area height and ``value`` is synchronized
    with the frontend value.
    """

    def __init__(
        self,
        value: str = "",
        *,
        label: str = "",
        placeholder: str = "",
        rows: int = 3,
        disabled: bool = False,
        **props: Any,
    ) -> None:
        super().__init__(
            "TextArea",
            label=label,
            value=value,
            disabled=disabled,
            props={"placeholder": placeholder, "rows": rows, **props},
        )


class AstryxNumberInput(AstryxWidget):
    """Render an Astryx numeric input.

    Use keyword props such as ``min``, ``max``, and ``step`` to constrain the
    numeric value when the underlying Astryx component supports them.
    """

    def __init__(self, value: int | float | None = None, *, label: str = "", disabled: bool = False, **props: Any) -> None:
        super().__init__("NumberInput", label=label, value=value, disabled=disabled, props=props)


class AstryxSlider(AstryxWidget):
    """Render an Astryx slider control.

    ``value`` may be a single number or a two-value range, depending on the
    Astryx slider props you pass through.
    """

    def __init__(
        self,
        value: int | float | tuple[int | float, int | float] | list[int | float] = 0,
        *,
        label: str = "",
        disabled: bool = False,
        **props: Any,
    ) -> None:
        super().__init__("Slider", label=label, value=value, disabled=disabled, props=props)


class AstryxCheckbox(AstryxWidget):
    """Render an Astryx checkbox input.

    ``value`` is the checked state. Use ``label`` for the visible checkbox
    label and ``disabled`` to make the input non-interactive.
    """

    def __init__(self, value: bool = False, *, label: str = "", disabled: bool = False, **props: Any) -> None:
        super().__init__("CheckboxInput", label=label, value=value, disabled=disabled, props=props)


class AstryxSwitch(AstryxWidget):
    """Render an Astryx switch for binary settings.

    Prefer this over a checkbox when the control immediately toggles a setting
    rather than selecting an item from a list.
    """

    def __init__(self, value: bool = False, *, label: str = "", disabled: bool = False, **props: Any) -> None:
        super().__init__("Switch", label=label, value=value, disabled=disabled, props=props)


class AstryxSelector(AstryxWidget):
    """Render a single-value Astryx selector.

    ``options`` can be a mapping, a sequence of ``(label, value)`` pairs, or a
    sequence of option dictionaries. The current ``value`` is synchronized with
    the frontend selected option.
    """

    def __init__(self, options: Iterable[Any] | Mapping[str, Any], value: str | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("Selector", label=label, value=value, props={"options": _option_records(options), **props})


class AstryxMultiSelector(AstryxWidget):
    """Render an Astryx selector that accepts multiple values.

    ``value`` should be an iterable of selected option values. ``options`` uses
    the same accepted shapes as :class:`AstryxSelector`.
    """

    def __init__(self, options: Iterable[Any] | Mapping[str, Any], value: Iterable[str] = (), *, label: str = "", **props: Any) -> None:
        super().__init__("MultiSelector", label=label, value=list(value), props={"options": _option_records(options), **props})


class AstryxDateInput(AstryxWidget):
    """Render an Astryx date input.

    Use ISO-style date strings for ``value`` when possible so notebook state is
    portable and easy to serialize.
    """

    def __init__(self, value: str | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("DateInput", label=label, value=value, props=props)


class AstryxTimeInput(AstryxWidget):
    """Render an Astryx time input.

    Use string values such as ``"09:30"`` for predictable notebook
    serialization.
    """

    def __init__(self, value: str | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("TimeInput", label=label, value=value, props=props)


class AstryxDateTimeInput(AstryxWidget):
    """Render an Astryx date-time input.

    ``value`` is synchronized as a JSON-safe value, typically an ISO date-time
    string.
    """

    def __init__(self, value: str | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("DateTimeInput", label=label, value=value, props=props)


class AstryxDateRangeInput(AstryxWidget):
    """Render an Astryx date-range input.

    Pass ``value`` as a mapping understood by Astryx, commonly containing start
    and end date strings.
    """

    def __init__(self, value: Mapping[str, str] | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("DateRangeInput", label=label, value=value, props=props)


class AstryxStack(AstryxWidget):
    """Arrange child widgets in an Astryx horizontal or vertical stack.

    ``children`` may be a list, tuple, mapping, or single widget. Use
    ``direction="horizontal"`` for a row and ``direction="vertical"`` for a
    column. Alignment props such as ``align`` and ``justify`` are forwarded to
    Astryx, and ``width="100%"`` is useful when composing card headers.
    """

    def __init__(self, children: ChildInput = None, *, direction: str = "vertical", gap: int | float = 2, **props: Any) -> None:
        super().__init__("Stack", children, props={"direction": direction, "gap": gap, **props})


class AstryxGrid(AstryxWidget):
    """Arrange child widgets in an Astryx grid.

    ``columns`` may be a fixed column count or an Astryx responsive column
    configuration. ``gap`` uses the Astryx spacing scale.
    """

    def __init__(self, children: ChildInput = None, *, columns: int | Mapping[str, Any] = 2, gap: int | float = 3, **props: Any) -> None:
        super().__init__("Grid", children, props={"columns": _clean_value(columns), "gap": gap, **props})


class AstryxCenter(AstryxWidget):
    """Center child content within its available space.

    Use this for empty states, spinners, or compact status blocks that should be
    visually centered in a notebook output area.
    """

    def __init__(self, children: ChildInput = None, *, axis: str = "both", **props: Any) -> None:
        super().__init__("Center", children, props={"axis": axis, **props})


class AstryxAspectRatio(AstryxWidget):
    """Constrain child content to a fixed aspect ratio.

    ``ratio`` is numeric, for example ``16 / 9``. This is useful for media,
    previews, or panels that need stable notebook dimensions.
    """

    def __init__(self, children: ChildInput = None, *, ratio: int | float = 16 / 9, **props: Any) -> None:
        super().__init__("AspectRatio", children, props={"ratio": ratio, **props})


class AstryxCard(AstryxWidget):
    """Render an Astryx card container.

    Use cards for discrete objects or self-contained panels. For structured
    card content, pass a single :class:`AstryxStack` child containing the title,
    divider, controls, and body rather than placing unrelated children directly
    in the card.
    """

    def __init__(self, children: ChildInput = None, *, variant: str = "default", **props: Any) -> None:
        super().__init__("Card", children, variant=variant, props={"variant": variant, **props})


class AstryxClickableCard(AstryxWidget):
    """Render an Astryx card that behaves like a clickable action target.

    ``label`` names the action for accessibility. Use ``callbacks`` for
    Python-side click handling.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        label: str,
        variant: str = "default",
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        **props: Any,
    ) -> None:
        super().__init__("ClickableCard", children, label=label, variant=variant, callbacks=callbacks, props={"variant": variant, **props})


class AstryxSelectableCard(AstryxWidget):
    """Render an Astryx card with a selected/unselected state.

    ``value`` is synchronized as the card selection state. Use this for choices
    that need more visual structure than a checkbox or radio item.
    """

    def __init__(self, children: ChildInput = None, value: bool = False, *, label: str, variant: str = "default", **props: Any) -> None:
        super().__init__("SelectableCard", children, label=label, value=value, variant=variant, props={"variant": variant, **props})


class AstryxSection(AstryxWidget):
    """Render an Astryx section container.

    Sections provide page-level grouping and are generally lighter-weight than
    cards for notebook layouts.
    """

    def __init__(self, children: ChildInput = None, *, variant: str = "section", **props: Any) -> None:
        super().__init__("Section", children, variant=variant, props={"variant": variant, **props})


class AstryxDivider(AstryxWidget):
    """Render an Astryx horizontal or vertical divider.

    Use dividers between related content blocks. In table panels, place the
    divider inside a vertical :class:`AstryxStack` between the title row and the
    table so it does not visually collide with table headers.
    """

    def __init__(self, *, orientation: str = "horizontal", variant: str = "subtle", **props: Any) -> None:
        super().__init__("Divider", variant=variant, props={"orientation": orientation, "variant": variant, **props})


class AstryxList(AstryxWidget):
    """Render an Astryx list from simple item records.

    ``items`` accepts strings, ``(label, value)`` pairs, mappings, or a mapping
    of labels to values. Item records are normalized before being sent to the
    frontend.
    """

    def __init__(self, items: Iterable[Any], *, header: str = "", **props: Any) -> None:
        super().__init__("List", props={"items": _option_records(items), "header": header or None, **props})


class AstryxMetadataList(AstryxWidget):
    """Render label/value metadata rows.

    ``items`` should contain mappings with label and value fields. This is
    useful for compact summaries next to tables or status panels.
    """

    def __init__(self, items: Iterable[Mapping[str, Any]], **props: Any) -> None:
        super().__init__("MetadataList", props={"items": _clean_value(list(items)), **props})


class AstryxBreadcrumbs(AstryxWidget):
    """Render Astryx breadcrumbs from item records.

    Each item can include ``label``, ``value``, ``href``, and current-item
    metadata supported by the frontend Breadcrumbs component.
    """

    def __init__(self, items: Iterable[Any], **props: Any) -> None:
        super().__init__("Breadcrumbs", props={"items": _option_records(items), **props})


class AstryxTabList(AstryxWidget):
    """Render an Astryx tab list.

    ``items`` defines the available tabs and ``value`` is the selected tab
    value. This wrapper renders the tab strip; content switching should be
    handled separately in Python or notebook layout code.
    """

    def __init__(self, items: Iterable[Any], value: str, **props: Any) -> None:
        super().__init__("TabList", value=value, props={"items": _option_records(items), **props})


class AstryxSegmentedControl(AstryxWidget):
    """Render a compact Astryx segmented control.

    Use this for small mutually exclusive option sets such as density, mode, or
    view selection.
    """

    def __init__(self, items: Iterable[Any], value: str, *, label: str, **props: Any) -> None:
        super().__init__("SegmentedControl", label=label, value=value, props={"items": _option_records(items), **props})


class AstryxRadioList(AstryxWidget):
    """Render a single-choice Astryx radio list.

    ``items`` uses normalized option records and ``value`` is the selected
    option value.
    """

    def __init__(self, items: Iterable[Any], value: str, *, label: str, **props: Any) -> None:
        super().__init__("RadioList", label=label, value=value, props={"items": _option_records(items), **props})


class AstryxCheckboxList(AstryxWidget):
    """Render a multi-choice Astryx checkbox list.

    ``value`` is an iterable of selected option values. Use this when each
    option can be toggled independently.
    """

    def __init__(self, items: Iterable[Any], value: Iterable[str] = (), *, label: str, **props: Any) -> None:
        super().__init__("CheckboxList", label=label, value=list(value), props={"items": _option_records(items), **props})


class AstryxButtonGroup(AstryxWidget):
    """Render an Astryx button group from item records.

    Each item can define a label, value, variant, or disabled state. Clicks send
    the selected item value back to Python callbacks.
    """

    def __init__(self, items: Iterable[Any], *, label: str, callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None, **props: Any) -> None:
        super().__init__("ButtonGroup", label=label, callbacks=callbacks, props={"items": _option_records(items), "label": label, **props})


class AstryxAvatarGroup(AstryxWidget):
    """Render a compact group of Astryx avatars.

    Parameters
    ----------
    items : iterable
        Avatar records. Strings are treated as names; mappings may include
        ``label``, ``name``, ``src``, ``alt``, and status metadata.
    overflow_count : int, default 0
        Number displayed in the generated overflow avatar. Leave at zero when
        every avatar is shown.
    **props : Any
        Additional Astryx ``AvatarGroup`` props such as ``size``.

    Notes
    -----
    This wrapper is useful for notebook summaries that need to show owners,
    reviewers, or participants without spending a full table column.
    """

    def __init__(self, items: Iterable[Any], *, overflow_count: int = 0, **props: Any) -> None:
        super().__init__("AvatarGroup", props={"items": _option_records(items), "overflowCount": overflow_count, **props})


class AstryxCode(AstryxWidget):
    """Render inline code with Astryx styling.

    Parameters
    ----------
    code : str
        Inline code text to render.
    **props : Any
        Additional Astryx ``Code`` props.

    See Also
    --------
    AstryxCodeBlock : Render multi-line syntax-highlighted code blocks.
    AstryxMarkdown : Render Markdown snippets that may contain inline code.
    """

    def __init__(self, code: str, **props: Any) -> None:
        super().__init__("Code", text=code, props=props)


class AstryxCitation(AstryxWidget):
    """Render a compact inline citation reference.

    Parameters
    ----------
    source : mapping
        Citation source metadata. Common fields are ``title``, ``url``, and
        ``icon``.
    number : int, default 1
        Citation number shown by the component.
    variant : {"number", "label"}, default "number"
        Astryx citation presentation variant.
    **props : Any
        Additional Astryx ``Citation`` props.

    Notes
    -----
    In notebooks, citations are best for compact references near model output,
    metrics, or generated summaries. Use a full link or metadata list for
    longer source details.
    """

    def __init__(self, source: Mapping[str, Any], *, number: int = 1, variant: str = "number", **props: Any) -> None:
        super().__init__("Citation", value=number, variant=variant, props={"source": _clean_value(source), "number": number, "variant": variant, **props})


class AstryxField(AstryxWidget):
    """Wrap a custom control with an Astryx field label and status area.

    Parameters
    ----------
    children : child input, optional
        Input widget or composed content to render inside the field.
    label : str
        Field label. Astryx requires a label for accessibility, even when the
        label is visually hidden.
    input_id : str, optional
        ID associated with the child input. A stable notebook-local ID is
        generated when omitted.
    description : str, default ""
        Supporting text rendered below the label.
    status : mapping, optional
        Status record such as ``{"type": "warning", "message": "Check"}``.
    disabled : bool, default False
        Whether the field should be styled as disabled.
    **props : Any
        Additional Astryx ``Field`` props.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        label: str,
        input_id: str = "",
        description: str = "",
        status: Mapping[str, Any] | None = None,
        disabled: bool = False,
        **props: Any,
    ) -> None:
        super().__init__(
            "Field",
            children,
            label=label,
            disabled=disabled,
            props={
                "label": label,
                "inputID": input_id,
                "description": description or None,
                "status": _clean_value(status) if status else None,
                **props,
            },
        )


class AstryxFieldStatus(AstryxWidget):
    """Render an Astryx field status message.

    Parameters
    ----------
    message : str
        Status text shown to the user.
    type : {"success", "warning", "error"}, default "success"
        Status severity.
    variant : {"attached", "detached"}, default "detached"
        Visual attachment style relative to a nearby field.
    **props : Any
        Additional Astryx ``FieldStatus`` props.
    """

    def __init__(self, message: str, *, type: str = "success", variant: str = "detached", **props: Any) -> None:
        super().__init__("FieldStatus", label=message, variant=type, props={"type": type, "message": message, "variant": variant, **props})


class AstryxFormLayout(AstryxWidget):
    """Arrange Astryx form controls with consistent field spacing.

    Parameters
    ----------
    children : child input, optional
        Form fields or controls to arrange.
    direction : {"vertical", "horizontal", "horizontal-labels"}, default "vertical"
        Astryx form layout direction.
    **props : Any
        Additional Astryx ``FormLayout`` props.

    Notes
    -----
    Use this instead of a generic grid when the content is semantically a form.
    It keeps notebook controls closer to the spacing and label alignment used
    by JupyterLab-style settings panels.
    """

    def __init__(self, children: ChildInput = None, *, direction: str = "vertical", **props: Any) -> None:
        super().__init__("FormLayout", children, props={"direction": direction, **props})


class AstryxInputGroup(AstryxWidget):
    """Group an input with prefix and suffix adornments.

    Parameters
    ----------
    children : child input, optional
        Usually an :class:`AstryxTextInput` or :class:`AstryxNumberInput`.
    label : str
        Accessible label for the grouped input.
    prefix : str, optional
        Text rendered before the child input, for example a currency symbol.
    suffix : str, optional
        Text rendered after the child input, for example a unit.
    disabled : bool, default False
        Whether the group should be styled as disabled.
    **props : Any
        Additional Astryx ``InputGroup`` props such as ``size``.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        label: str,
        prefix: str = "",
        suffix: str = "",
        disabled: bool = False,
        **props: Any,
    ) -> None:
        super().__init__(
            "InputGroup",
            children,
            label=label,
            disabled=disabled,
            props={"label": label, "prefix": prefix or None, "suffix": suffix or None, **props},
        )


class AstryxCollapsible(AstryxWidget):
    """Render expandable notebook content.

    Parameters
    ----------
    children : child input, optional
        Content shown when the disclosure is open.
    trigger : str
        Text shown in the always-visible trigger area.
    default_open : bool, default True
        Initial open state for the uncontrolled Astryx component.
    value : str, optional
        Identifier used by Astryx collapsible groups.
    **props : Any
        Additional Astryx ``Collapsible`` props.

    Notes
    -----
    This is useful for hiding verbose diagnostics, raw JSON, parameter blocks,
    or explanatory detail while keeping the main notebook output scannable.
    """

    def __init__(self, children: ChildInput = None, *, trigger: str, default_open: bool = True, value: str = "", **props: Any) -> None:
        super().__init__(
            "Collapsible",
            children,
            label=trigger,
            props={"trigger": trigger, "defaultIsOpen": default_open, "value": value or None, **props},
        )


class AstryxOutline(AstryxWidget):
    """Render a table-of-contents outline.

    Parameters
    ----------
    items : iterable of mapping
        Outline records with ``id``, ``label``, and ``level`` fields.
    active_id : str, optional
        Currently active heading ID. When set, the value is synchronized back
        to Python on frontend changes.
    label : str, default "Table of contents"
        Accessible label for the outline navigation.
    density : {"default", "compact"}, default "compact"
        Item spacing density.
    **props : Any
        Additional Astryx ``Outline`` props.
    """

    def __init__(self, items: Iterable[Mapping[str, Any]], *, active_id: str = "", label: str = "Table of contents", density: str = "compact", **props: Any) -> None:
        super().__init__(
            "Outline",
            label=label,
            value=active_id,
            props={"items": _clean_value(list(items)), "label": label, "density": density, **props},
        )


class AstryxTreeList(AstryxWidget):
    """Render hierarchical notebook data as an expandable tree.

    Parameters
    ----------
    items : iterable of mapping
        Recursive tree records. Each record should contain ``id`` and
        ``label`` and may include ``children``, ``description``, ``href``,
        ``isSelected``, and ``isExpanded``.
    header : str, optional
        Optional header rendered above the tree.
    density : {"compact", "balanced", "spacious"}, default "balanced"
        Astryx row density.
    **props : Any
        Additional Astryx ``TreeList`` props.

    Notes
    -----
    Tree lists are helpful for datasets, model artifacts, report sections, and
    file-like hierarchies that would be too noisy as a flat table.
    """

    def __init__(self, items: Iterable[Mapping[str, Any]], *, header: str = "", density: str = "balanced", **props: Any) -> None:
        super().__init__("TreeList", props={"items": _clean_value(list(items)), "header": header or None, "density": density, **props})


class AstryxToolbar(AstryxWidget):
    """Render an Astryx toolbar with optional start, center, and end slots.

    Parameters
    ----------
    children : child input, optional
        Toolbar content. When a mapping is provided, keys named ``"start"``,
        ``"center"``, and ``"end"`` are used as Astryx toolbar slots.
    label : str
        Accessible toolbar label.
    size : {"sm", "md", "lg"}, default "sm"
        Size inherited by compatible toolbar controls.
    gap : int or float, default 1
        Astryx spacing step between toolbar items.
    **props : Any
        Additional Astryx ``Toolbar`` props such as ``variant`` or
        ``dividers``.
    """

    def __init__(self, children: ChildInput = None, *, label: str, size: str = "sm", gap: int | float = 1, **props: Any) -> None:
        super().__init__("Toolbar", children, label=label, props={"label": label, "size": size, "gap": gap, **props})


class AstryxTooltip(AstryxWidget):
    """Attach a tooltip to notebook content.

    Parameters
    ----------
    content : str or child input
        Tooltip content. Keep this concise because tooltips are intended for
        short hover or focus hints.
    trigger : child input, optional
        Trigger widget or text. When a mapping is used, key ``"trigger"`` is
        treated as the trigger and key ``"content"`` can override ``content``.
    label : str, optional
        Fallback text content when ``content`` is empty.
    **props : Any
        Additional Astryx ``Tooltip`` props such as ``placement`` or
        ``hasHoverIndication``.
    """

    def __init__(self, content: str | ChildInput, trigger: ChildInput = None, *, label: str = "", **props: Any) -> None:
        children = {"trigger": trigger} if trigger is not None else None
        if not isinstance(content, str):
            children = {"trigger": trigger, "content": content} if trigger is not None else {"content": content}
            content_prop = None
        else:
            content_prop = content
        super().__init__("Tooltip", children, label=label or content_prop or "", props={"content": content_prop, **props})


class AstryxHoverCard(AstryxWidget):
    """Attach a hover card with richer preview content.

    Parameters
    ----------
    content : str or child input
        Preview content shown in the hover layer.
    trigger : child input
        Trigger widget or text that opens the hover card.
    label : str, optional
        Accessible fallback label.
    **props : Any
        Additional Astryx ``HoverCard`` props such as ``placement`` and
        ``delay``.
    """

    def __init__(self, content: str | ChildInput, trigger: ChildInput, *, label: str = "", **props: Any) -> None:
        children = {"trigger": trigger}
        content_prop: str | None = content if isinstance(content, str) else None
        if not isinstance(content, str):
            children["content"] = content
        super().__init__("HoverCard", children, label=label or content_prop or "", props={"content": content_prop, **props})


class AstryxPopover(AstryxWidget):
    """Render click-triggered popover content.

    Parameters
    ----------
    content : str or child input
        Popover body content. Child widgets can be used for interactive
        controls.
    trigger : child input
        Trigger widget, typically an :class:`AstryxButton` or
        :class:`AstryxIconButton`.
    label : str
        Accessible label for the popover dialog.
    **props : Any
        Additional Astryx ``Popover`` props such as ``placement`` or ``width``.
    """

    def __init__(self, content: str | ChildInput, trigger: ChildInput, *, label: str, **props: Any) -> None:
        children = {"trigger": trigger}
        content_prop: str | None = content if isinstance(content, str) else None
        if not isinstance(content, str):
            children["content"] = content
        super().__init__("Popover", children, label=label, props={"content": content_prop, "label": label, **props})


class AstryxDropdownMenu(AstryxWidget):
    """Render a button-backed Astryx dropdown menu.

    Parameters
    ----------
    items : iterable
        Menu records. Strings become actions; mappings may include ``label``,
        ``value``, ``icon``, ``disabled``, or Astryx section/divider records.
    label : str
        Button label and accessible menu trigger label.
    variant : str, default "secondary"
        Astryx button variant used by the trigger.
    disabled : bool, default False
        Whether the menu trigger is disabled.
    callbacks : iterable of callable, optional
        Python callbacks invoked when a menu item is clicked.
    **props : Any
        Additional Astryx ``DropdownMenu`` props.
    """

    def __init__(
        self,
        items: Iterable[Any],
        *,
        label: str,
        variant: str = "secondary",
        disabled: bool = False,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "DropdownMenu",
            label=label,
            variant=variant,
            disabled=disabled,
            callbacks=callbacks,
            props={"items": _option_records(items), "button": {"label": label, "variant": variant}, **props},
        )


class AstryxMoreMenu(AstryxWidget):
    """Render a compact overflow action menu.

    Parameters
    ----------
    items : iterable
        Menu records using the same shape as :class:`AstryxDropdownMenu`.
    label : str, default "More options"
        Accessible label for the icon-only trigger.
    variant : str, default "ghost"
        Astryx trigger button variant.
    disabled : bool, default False
        Whether the menu trigger is disabled.
    callbacks : iterable of callable, optional
        Python callbacks invoked when a menu item is clicked.
    **props : Any
        Additional Astryx ``MoreMenu`` props such as ``size``.
    """

    def __init__(
        self,
        items: Iterable[Any],
        *,
        label: str = "More options",
        variant: str = "ghost",
        disabled: bool = False,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "MoreMenu",
            label=label,
            variant=variant,
            disabled=disabled,
            callbacks=callbacks,
            props={"items": _option_records(items), "label": label, "variant": variant, **props},
        )


class AstryxCalendar(AstryxWidget):
    """Render an Astryx calendar date picker.

    Parameters
    ----------
    value : str or mapping, optional
        Selected date for single mode or a date-range mapping for range mode.
    mode : {"single", "range"}, default "single"
        Calendar selection mode.
    **props : Any
        Additional Astryx ``Calendar`` props such as ``min``, ``max``,
        ``numberOfMonths``, or ``hasWeekNumbers``.
    """

    def __init__(self, value: str | Mapping[str, str] | None = None, *, mode: str = "single", **props: Any) -> None:
        super().__init__("Calendar", value=value, props={"mode": mode, **props})


class AstryxFileInput(AstryxWidget):
    """Render an Astryx file input.

    Parameters
    ----------
    label : str
        Accessible file input label.
    value : object, optional
        Initial synchronized value. Frontend selections synchronize file
        metadata records, not file bytes.
    multiple : bool, default False
        Whether users may select more than one file.
    disabled : bool, default False
        Whether the file input is disabled.
    **props : Any
        Additional Astryx ``FileInput`` props such as ``accept``, ``mode``, or
        ``maxSize``.

    Notes
    -----
    Notebook kernels receive file metadata only. Uploading file contents should
    be implemented as a separate explicit workflow.
    """

    def __init__(self, *, label: str, value: Any = None, multiple: bool = False, disabled: bool = False, **props: Any) -> None:
        super().__init__("FileInput", label=label, value=value, disabled=disabled, props={"label": label, "isMultiple": multiple, **props})


# TODO(astryx): Candidate follow-ups after the notebook-safe wrappers above:
# - study a reusable brand/theme identity API so notebooks can define shared
#   colors, typography, and component variants without per-widget styling props;
# - consider data-entry wrappers with richer state synchronization
#   (Tokenizer, Typeahead, CommandPalette) once frontend search-source semantics
#   and Python callback contracts are confirmed;
# - evaluate modal/dialog-style components (Dialog, AlertDialog) in JupyterLab
#   output areas before exposing stable wrappers.


class AstryxTable(AstryxWidget):
    """Render a data-driven Astryx table for notebook use.

    ``rows`` may contain mappings, sequences, or scalar values. ``columns`` may
    be omitted, a mapping of keys to headers, a sequence of keys, or full column
    dictionaries. Row checkbox selection is optional: leave ``selects`` empty
    for no checkbox column, use ``selects="multiple"`` for multi-select, or
    ``selects="single"`` for one selected row. Sorting is optional and enabled
    with ``sortable=True`` or sortable column definitions. Astryx row striping
    is off by default; pass ``isStriped=True`` only when shaded alternate rows
    are desired.
    """

    selected = t.List(t.Unicode(), default_value=[]).tag(sync=True)
    selects = t.Unicode("").tag(sync=True)
    sort_key = t.Unicode("").tag(sync=True)
    sort_direction = t.Unicode("").tag(sync=True)
    sortable = t.Bool(False).tag(sync=True)
    select_all_label = t.Unicode("Select all rows").tag(sync=True)

    def __init__(
        self,
        rows: Iterable[Any] = (),
        columns: Iterable[Any] | Mapping[str, Any] | None = None,
        *,
        row_key: str | None = "id",
        selected: Iterable[Any] = (),
        selects: str = "",
        sortable: bool = False,
        sort_key: str = "",
        sort_direction: str = "",
        select_all_label: str = "Select all rows",
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        **props: Any,
    ) -> None:
        row_list = list(rows)
        column_list = _table_columns(columns, row_list)
        self._row_key = row_key or "__row_id"
        super().__init__(
            "Table",
            props={
                "rows": _table_rows(row_list, column_list, self._row_key),
                "columns": column_list,
                "idKey": self._row_key,
                **props,
            },
            selected=[str(item) for item in selected],
            selects=selects,
            sortable=sortable,
            sort_key=sort_key,
            sort_direction=sort_direction,
            select_all_label=select_all_label,
            width=width,
            height=height,
        )
        self._selection_callbacks: list[Callable[[AstryxTable], None]] = []
        self._sort_callbacks: list[Callable[[AstryxTable], None]] = []

    @property
    def rows(self) -> list[dict[str, Any]]:
        """Current normalized Astryx table rows."""
        return list(self.props.get("rows", []))

    @property
    def columns(self) -> list[dict[str, Any]]:
        """Current Astryx table column definitions."""
        return list(self.props.get("columns", []))

    @property
    def row_key(self) -> str:
        """Current row id property used by Astryx Table."""
        return str(self.props.get("idKey", self._row_key))

    def set_rows(
        self,
        rows: Iterable[Any],
        *,
        columns: Iterable[Any] | Mapping[str, Any] | None = None,
        row_key: str | None = None,
    ) -> None:
        """Replace table rows from raw row mappings, sequences, or scalar values."""
        row_list = list(rows)
        if row_key is not None:
            self._row_key = row_key or "__row_id"
        column_list = _table_columns(columns, row_list) if columns is not None or not self.columns else self.columns
        self._set_table_props(rows=_table_rows(row_list, column_list, self._row_key), columns=column_list, idKey=self._row_key)
        self._drop_missing_selection()

    def append_row(self, row: Any, *, row_key: str | None = None) -> str:
        """Append one raw row and return its normalized row id."""
        normalized = self._normalize_new_row(row, row_key)
        self._set_table_props(rows=[*self.rows, normalized])
        return str(normalized[self.row_key])

    def prepend_row(self, row: Any, *, row_key: str | None = None) -> str:
        """Prepend one raw row and return its normalized row id."""
        normalized = self._normalize_new_row(row, row_key)
        self._set_table_props(rows=[normalized, *self.rows])
        return str(normalized[self.row_key])

    def update_row(self, row_value: Any, values: Any) -> None:
        """Update cells for an existing row by row id."""
        target = str(row_value)
        next_rows = []
        found = False
        for row in self.rows:
            if str(row.get(self.row_key)) != target:
                next_rows.append(row)
                continue
            found = True
            next_rows.append(self._updated_row(row, values))
        if not found:
            msg = f"table row not found: {target}"
            raise KeyError(msg)
        self._set_table_props(rows=next_rows)

    def remove_row(self, row_value: Any) -> None:
        """Remove an existing row by row id."""
        target = str(row_value)
        next_rows = [row for row in self.rows if str(row.get(self.row_key)) != target]
        if len(next_rows) == len(self.rows):
            msg = f"table row not found: {target}"
            raise KeyError(msg)
        self._set_table_props(rows=next_rows)
        if target in self.selected:
            self.selected = [item for item in self.selected if item != target]

    def on_select(
        self,
        callback: Callable[[AstryxTable], None],
        remove: bool = False,
    ) -> None:
        """Register or unregister a callback for table selection changes."""
        if remove:
            self._selection_callbacks = [item for item in self._selection_callbacks if item is not callback]
            return
        self._selection_callbacks.append(callback)

    def on_sort(
        self,
        callback: Callable[[AstryxTable], None],
        remove: bool = False,
    ) -> None:
        """Register or unregister a callback for table sort changes."""
        if remove:
            self._sort_callbacks = [item for item in self._sort_callbacks if item is not callback]
            return
        self._sort_callbacks.append(callback)

    def _normalize_new_row(self, row: Any, row_key: str | None = None) -> dict[str, Any]:
        if row_key is not None:
            self._row_key = row_key or "__row_id"
            self._set_table_props(idKey=self._row_key)
        columns = self.columns
        if not columns:
            columns = _table_columns(None, [row])
            self._set_table_props(columns=columns)
        normalized = _table_rows([row], columns, self._row_key)[0]
        if row_key is None and self._row_key == "__row_id":
            existing_values = {str(existing.get(self._row_key)) for existing in self.rows}
            next_index = len(self.rows)
            while str(next_index) in existing_values:
                next_index += 1
            normalized[self._row_key] = str(next_index)
        row_value = str(normalized.get(self._row_key))
        if any(str(existing.get(self._row_key)) == row_value for existing in self.rows):
            msg = f"table row already exists: {row_value}"
            raise ValueError(msg)
        return normalized

    def _updated_row(self, row: Mapping[str, Any], values: Any) -> dict[str, Any]:
        updated = dict(row)
        if isinstance(values, Mapping):
            source = values.get("cells") if isinstance(values.get("cells"), Mapping) else values
            for column in self.columns:
                key = column["key"]
                if key in source:
                    updated[key] = _clean_value(source[key])
            if self.row_key in source:
                updated[self.row_key] = _clean_value(source[self.row_key])
            return updated

        if isinstance(values, (list, tuple)):
            for index, column in enumerate(self.columns):
                if index < len(values):
                    updated[column["key"]] = _clean_value(values[index])
            return updated

        if self.columns:
            updated[self.columns[0]["key"]] = _clean_value(values)
        return updated

    def _set_table_props(self, **updates: Any) -> None:
        self.props = {**self.props, **_clean_props(updates)}

    def _drop_missing_selection(self) -> None:
        row_values = {str(row.get(self.row_key)) for row in self.rows}
        self.selected = [item for item in self.selected if item in row_values]

    def _handle_frontend_message(self, _widget: object, content: dict[str, Any], _buffers: object) -> None:
        msg_type = content.get("type")
        if msg_type == "selection":
            for callback in list(self._selection_callbacks):
                callback(self)
            return
        if msg_type == "sort":
            for callback in list(self._sort_callbacks):
                callback(self)
            return
        super()._handle_frontend_message(_widget, content, _buffers)


class AstryxEmptyState(AstryxWidget):
    """Render an Astryx empty-state message.

    Use ``title`` for the primary message and ``description`` for supporting
    context when a table, list, or panel has no content.
    """

    def __init__(self, title: str, *, description: str = "", **props: Any) -> None:
        super().__init__("EmptyState", props={"title": title, "description": description, **props})


class AstryxBanner(AstryxWidget):
    """Render an Astryx banner for prominent status messages.

    ``status`` controls the visual treatment, for example informational,
    success, warning, or error states supported by Astryx.
    """

    def __init__(self, title: str, *, status: str = "info", description: str = "", **props: Any) -> None:
        super().__init__("Banner", label=title, props={"title": title, "status": status, "description": description, **props})


class AstryxStatusDot(AstryxWidget):
    """Render an inline Astryx status indicator.

    Use this for compact connection, health, or workflow states. ``label`` is
    visible text and ``variant`` selects the status color.
    """

    def __init__(self, label: str, *, variant: str = "neutral", **props: Any) -> None:
        super().__init__("StatusDot", label=label, variant=variant, props=props)


class AstryxProgressBar(AstryxWidget):
    """Render an Astryx progress bar.

    ``value`` is the numeric progress value and ``label`` names the progress
    region for both visible text and accessibility.
    """

    def __init__(self, value: int | float = 0, *, label: str, variant: str = "accent", **props: Any) -> None:
        super().__init__("ProgressBar", label=label, value=value, variant=variant, props=props)


class AstryxSpinner(AstryxWidget):
    """Render an Astryx loading spinner.

    Provide a concise ``label`` so the loading state remains accessible in
    notebook output.
    """

    def __init__(self, *, label: str = "Loading", **props: Any) -> None:
        super().__init__("Spinner", label=label, props={"label": label, **props})


class AstryxSkeleton(AstryxWidget):
    """Render an Astryx skeleton placeholder.

    Use ``width`` and ``height`` to reserve stable notebook space while content
    is loading.
    """

    def __init__(self, *, width: int | str = "100%", height: int | str = 16, **props: Any) -> None:
        super().__init__("Skeleton", props={"width": width, "height": height, **props})


class AstryxToken(AstryxWidget):
    """Render an Astryx token or chip.

    Tokens are compact labels for filters, tags, or selected values. Additional
    props can make tokens removable or clickable when supported by Astryx.
    """

    def __init__(self, label: str, *, color: str = "default", **props: Any) -> None:
        super().__init__("Token", label=label, props={"color": color, **props})


class AstryxKbd(AstryxWidget):
    """Render keyboard shortcut text with Astryx styling.

    ``keys`` is the shortcut sequence to display, for example ``"Cmd+K"``.
    """

    def __init__(self, keys: str, **props: Any) -> None:
        super().__init__("Kbd", props={"keys": keys, **props})


class AstryxLink(AstryxWidget):
    """Render an Astryx text link.

    ``label`` is the visible link text and ``href`` is the destination URL. Use
    an empty ``href`` only for non-navigation link-like actions.
    """

    def __init__(self, label: str, *, href: str = "", **props: Any) -> None:
        super().__init__("Link", text=label, label=label, props={"href": href or None, **props})


class AstryxAvatar(AstryxWidget):
    """Render an Astryx avatar.

    ``name`` is used for initials, alt text, and fallback identity metadata.
    """

    def __init__(self, name: str, **props: Any) -> None:
        super().__init__("Avatar", label=name, props={"name": name, **props})


class AstryxIcon(AstryxWidget):
    """Render an Astryx icon by name.

    Use icon names supported by the Astryx icon set. Prefer icon buttons for
    interactive icon-only actions.
    """

    def __init__(self, icon: str, **props: Any) -> None:
        super().__init__("Icon", text=icon, icon=icon, props={"icon": icon, **props})


class AstryxThumbnail(AstryxWidget):
    """Render an Astryx thumbnail image or media placeholder.

    ``src`` is optional; ``label`` and ``alt`` provide accessible fallback text
    when no image is available.
    """

    def __init__(self, *, label: str = "", src: str = "", alt: str = "", **props: Any) -> None:
        super().__init__("Thumbnail", label=label, props={"src": src or None, "alt": alt or label, "label": label, **props})


class AstryxCodeBlock(AstryxWidget):
    """Render syntax-highlighted code with Astryx styling.

    ``code`` is the source text and ``language`` names the syntax highlighter
    language, such as ``"python"`` or ``"json"``.
    """

    def __init__(self, code: str, *, language: str = "python", **props: Any) -> None:
        super().__init__("CodeBlock", props={"code": code, "language": language, **props})


class AstryxMarkdown(AstryxWidget):
    """Render Markdown content through the Astryx Markdown component.

    Use this for short trusted Markdown snippets in notebook output. The text
    is passed to the frontend Markdown renderer.
    """

    def __init__(self, text: str, **props: Any) -> None:
        super().__init__("Markdown", text=text, props=props)


class AstryxBlockquote(AstryxWidget):
    """Render quoted text with Astryx blockquote styling.

    Use this for excerpts, callouts, or quoted notes that should remain visually
    distinct from body text.
    """

    def __init__(self, text: str, **props: Any) -> None:
        super().__init__("Blockquote", text=text, props=props)


class AstryxTimestamp(AstryxWidget):
    """Render a timestamp value with Astryx formatting.

    ``value`` can be a string or numeric timestamp accepted by the frontend
    component.
    """

    def __init__(self, value: str | int | float, **props: Any) -> None:
        super().__init__("Timestamp", value=value, props=props)


__all__ = [
    "AstryxAspectRatio",
    "AstryxAvatar",
    "AstryxAvatarGroup",
    "AstryxBadge",
    "AstryxBanner",
    "AstryxBlockquote",
    "AstryxBreadcrumbs",
    "AstryxButton",
    "AstryxButtonGroup",
    "AstryxCalendar",
    "AstryxCard",
    "AstryxCenter",
    "AstryxCheckbox",
    "AstryxCheckboxList",
    "AstryxClickableCard",
    "AstryxCitation",
    "AstryxCode",
    "AstryxCodeBlock",
    "AstryxComponent",
    "AstryxCollapsible",
    "AstryxDropdownMenu",
    "AstryxDateInput",
    "AstryxDateRangeInput",
    "AstryxDateTimeInput",
    "AstryxDivider",
    "AstryxEmptyState",
    "AstryxField",
    "AstryxFieldStatus",
    "AstryxFileInput",
    "AstryxFormLayout",
    "AstryxGrid",
    "AstryxHoverCard",
    "AstryxHeading",
    "AstryxIcon",
    "AstryxIconButton",
    "AstryxInputGroup",
    "AstryxKbd",
    "AstryxLink",
    "AstryxList",
    "AstryxMarkdown",
    "AstryxMetadataList",
    "AstryxMoreMenu",
    "AstryxMultiSelector",
    "AstryxNumberInput",
    "AstryxOutline",
    "AstryxProgressBar",
    "AstryxPopover",
    "AstryxRadioList",
    "AstryxSection",
    "AstryxSegmentedControl",
    "AstryxSelectableCard",
    "AstryxSelector",
    "AstryxSkeleton",
    "AstryxSlider",
    "AstryxSpinner",
    "AstryxStack",
    "AstryxStatusDot",
    "AstryxSwitch",
    "AstryxTabList",
    "AstryxTable",
    "AstryxText",
    "AstryxTextArea",
    "AstryxTextInput",
    "AstryxThumbnail",
    "AstryxTimeInput",
    "AstryxTimestamp",
    "AstryxToggleButton",
    "AstryxToken",
    "AstryxToolbar",
    "AstryxTooltip",
    "AstryxTreeList",
    "AstryxWidget",
]
