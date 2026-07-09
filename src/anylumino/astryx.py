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


def _clean_brand(brand: Mapping[str, Any] | None) -> dict[str, Any]:
    if not brand:
        return {}
    if "tokens" in brand:
        return {"name": str(brand.get("name", "anylumino-brand")), "tokens": _clean_props(brand.get("tokens"))}
    tokens = {key: value for key, value in brand.items() if key != "name"}
    return {"name": str(brand.get("name", "anylumino-brand")), "tokens": _clean_props(tokens)}


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


def _search_records(items: Iterable[Any] | Mapping[str, Any]) -> list[dict[str, Any]]:
    records = _option_records(items)
    normalized = []
    for index, item in enumerate(records):
        if isinstance(item, Mapping):
            label = str(item.get("label", item.get("value", item.get("id", index))))
            value = str(item.get("id", item.get("value", label)))
            normalized.append({**_clean_value(item), "id": value, "label": label})
        else:
            normalized.append({"id": str(item), "label": str(item)})
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
    """Base anywidget for Astryx-backed components.

    Parameters
    ----------
    component_name : str, default 'Stack'
        Frontend Astryx component name registered in the anylumino bridge.
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    props : Mapping[str, Any] | None
        Additional Astryx component props serialized to the frontend.
    text : str, default ''
        Text content synchronized to the frontend component.
    label : str, default ''
        Visible or accessible label for the component.
    value : Any
        Synchronized component value.
    disabled : bool, default False
        Whether the component should render disabled.
    variant : str, default ''
        Astryx visual variant.
    brand : Mapping[str, Any] | None
        Reusable Astryx brand token mapping.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    **kwargs : Any
        Additional widget trait values."""

    _esm = static_asset("astryx/astryx_widget.bundle.js")
    _css = static_asset("astryx/astryx_widget.bundle.css")

    component_family = t.Unicode("astryx").tag(sync=True)
    component_name = t.Unicode("Stack").tag(sync=True)
    props = t.Dict(default_value={}).tag(sync=True)
    color_mode = t.Unicode("light").tag(sync=True)
    theme = t.Unicode("neutral").tag(sync=True)
    brand = t.Dict(default_value={}).tag(sync=True)

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
        brand: Mapping[str, Any] | None = None,
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
            brand=_clean_brand(brand),
            callbacks=callbacks,
            **kwargs,
        )

    def apply_brand(self, brand: Mapping[str, Any] | None, *, color_mode: str | None = None) -> None:
        """Apply a reusable Astryx brand identity to this widget subtree."""
        self.brand = _clean_brand(brand)
        if color_mode is not None:
            self.color_mode = color_mode
        for child in self.widgets:
            if isinstance(child, AstryxWidget):
                child.apply_brand(self.brand, color_mode=color_mode)


def AstryxBrand(name: str = "anylumino-brand", **tokens: Any) -> dict[str, Any]:
    """Create a reusable Astryx brand token mapping.

    Parameters
    ----------
    name : str, default "anylumino-brand"
        Name assigned to the runtime Astryx theme.
    **tokens : Any
        Astryx design tokens. Names may include or omit the leading ``"--"``.
        Values may be strings or two-item ``(light, dark)`` tuples.

    Returns
    -------
    dict
        JSON-safe brand record that can be passed to :class:`AstryxTheme` or
        :meth:`AstryxWidget.apply_brand`.
    """
    return _clean_brand({"name": name, "tokens": tokens})


class AstryxComponent(AstryxWidget):
    """Render a registered Astryx component by name.

    Parameters
    ----------
    component_name : str
        Frontend Astryx component name registered in the anylumino bridge.
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    props : Mapping[str, Any] | None
        Additional Astryx component props serialized to the frontend.
    text : str, default ''
        Text content synchronized to the frontend component.
    label : str, default ''
        Visible or accessible label for the component.
    **kwargs : Any
        Additional widget trait values."""

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


class AstryxTheme(AstryxWidget):
    """Apply a reusable Astryx brand identity to child widgets.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    brand : Mapping[str, Any] | None
        Reusable Astryx brand token mapping.
    color_mode : str, default 'light'
        Astryx color mode for this component or subtree.
    direction : str, default 'vertical'
        Layout direction.
    gap : int | float, default 2
        Astryx spacing step between children.
    **props : Any
        Additional Astryx component props serialized to the frontend.

    Notes
    -----
    This wrapper propagates brand tokens to nested Astryx child widgets
    because each anywidget renders in its own frontend root.
    """

    def __init__(
        self,
        children: ChildInput = None,
        *,
        brand: Mapping[str, Any] | None = None,
        color_mode: str = "light",
        direction: str = "vertical",
        gap: int | float = 2,
        **props: Any,
    ) -> None:
        super().__init__(
            "Stack",
            children,
            props={"direction": direction, "gap": gap, **props},
            brand=brand,
            color_mode=color_mode,
        )
        self.apply_brand(brand, color_mode=color_mode)


class AstryxText(AstryxWidget):
    """Render themed Astryx body text.

    Parameters
    ----------
    text : str
        Text content synchronized to the frontend component.
    props : Mapping[str, Any] | None
        Additional Astryx component props serialized to the frontend.
    **kwargs : Any
        Additional widget trait values."""

    def __init__(self, text: str, *, props: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__("Text", text=text, props=props, **kwargs)


class AstryxHeading(AstryxWidget):
    """Render a semantic Astryx heading.

    Parameters
    ----------
    text : str
        Text content synchronized to the frontend component.
    level : int, default 3
        Heading level from 1 through 6.
    props : Mapping[str, Any] | None
        Additional Astryx component props serialized to the frontend.
    **kwargs : Any
        Additional widget trait values."""

    def __init__(self, text: str, *, level: int = 3, props: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        if not 1 <= level <= 6:
            raise ValueError("heading level must be between 1 and 6")
        super().__init__("Heading", text=text, props={"level": level, **dict(props or {}), **kwargs})


class AstryxBadge(AstryxWidget):
    """Render a compact status or category badge.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    variant : str, default 'neutral'
        Astryx visual variant.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, label: str, *, variant: str = "neutral", **props: Any) -> None:
        super().__init__("Badge", label=label, variant=variant, props=props)


class AstryxButton(AstryxWidget):
    """Render an Astryx push button.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    variant : str, default 'secondary'
        Astryx visual variant.
    disabled : bool, default False
        Whether the component should render disabled.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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
    """Render an icon-only Astryx button.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    icon : str, default 'close'
        Astryx icon name.
    variant : str, default 'secondary'
        Astryx visual variant.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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

    Parameters
    ----------
    value : bool, default False
        Synchronized component value.
    label : str
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the component should render disabled.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, value: bool = False, *, label: str, disabled: bool = False, **props: Any) -> None:
        super().__init__("ToggleButton", label=label, value=value, disabled=disabled, props=props)


class AstryxTextInput(AstryxWidget):
    """Render a single-line Astryx text input.

    Parameters
    ----------
    value : str, default ''
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    placeholder : str, default ''
        Placeholder text shown when the control is empty.
    disabled : bool, default False
        Whether the component should render disabled.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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

    Parameters
    ----------
    value : str, default ''
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    placeholder : str, default ''
        Placeholder text shown when the control is empty.
    rows : int, default 3
        Rows or records rendered by the component.
    disabled : bool, default False
        Whether the component should render disabled.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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

    Parameters
    ----------
    value : int | float | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the component should render disabled.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, value: int | float | None = None, *, label: str = "", disabled: bool = False, **props: Any) -> None:
        super().__init__("NumberInput", label=label, value=value, disabled=disabled, props=props)


class AstryxSlider(AstryxWidget):
    """Render an Astryx slider control.

    Parameters
    ----------
    value : int | float | tuple[int | float, int | float] | list[int | float], default 0
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the component should render disabled.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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

    Parameters
    ----------
    value : bool, default False
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the component should render disabled.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, value: bool = False, *, label: str = "", disabled: bool = False, **props: Any) -> None:
        super().__init__("CheckboxInput", label=label, value=value, disabled=disabled, props=props)


class AstryxSwitch(AstryxWidget):
    """Render an Astryx switch for binary settings.

    Parameters
    ----------
    value : bool, default False
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    disabled : bool, default False
        Whether the component should render disabled.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, value: bool = False, *, label: str = "", disabled: bool = False, **props: Any) -> None:
        super().__init__("Switch", label=label, value=value, disabled=disabled, props=props)


class AstryxSelector(AstryxWidget):
    """Render a single-value Astryx selector.

    Parameters
    ----------
    options : Iterable[Any] | Mapping[str, Any]
        Option records. Mappings, pairs, strings, and dictionaries are normalized.
    value : str | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, options: Iterable[Any] | Mapping[str, Any], value: str | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("Selector", label=label, value=value, props={"options": _option_records(options), **props})


class AstryxMultiSelector(AstryxWidget):
    """Render an Astryx selector that accepts multiple values.

    Parameters
    ----------
    options : Iterable[Any] | Mapping[str, Any]
        Option records. Mappings, pairs, strings, and dictionaries are normalized.
    value : Iterable[str], default ()
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, options: Iterable[Any] | Mapping[str, Any], value: Iterable[str] = (), *, label: str = "", **props: Any) -> None:
        super().__init__("MultiSelector", label=label, value=list(value), props={"options": _option_records(options), **props})


class AstryxDateInput(AstryxWidget):
    """Render an Astryx date input.

    Parameters
    ----------
    value : str | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, value: str | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("DateInput", label=label, value=value, props=props)


class AstryxTimeInput(AstryxWidget):
    """Render an Astryx time input.

    Parameters
    ----------
    value : str | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, value: str | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("TimeInput", label=label, value=value, props=props)


class AstryxDateTimeInput(AstryxWidget):
    """Render an Astryx date-time input.

    Parameters
    ----------
    value : str | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, value: str | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("DateTimeInput", label=label, value=value, props=props)


class AstryxDateRangeInput(AstryxWidget):
    """Render an Astryx date-range input.

    Parameters
    ----------
    value : Mapping[str, str] | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, value: Mapping[str, str] | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("DateRangeInput", label=label, value=value, props=props)


class AstryxStack(AstryxWidget):
    """Arrange child widgets in an Astryx stack.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    direction : str, default 'vertical'
        Layout direction.
    gap : int | float, default 2
        Astryx spacing step between children.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, children: ChildInput = None, *, direction: str = "vertical", gap: int | float = 2, **props: Any) -> None:
        super().__init__("Stack", children, props={"direction": direction, "gap": gap, **props})


class AstryxGrid(AstryxWidget):
    """Arrange child widgets in an Astryx grid.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    columns : int | Mapping[str, Any], default 2
        Grid or table column definition.
    gap : int | float, default 3
        Astryx spacing step between children.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, children: ChildInput = None, *, columns: int | Mapping[str, Any] = 2, gap: int | float = 3, **props: Any) -> None:
        super().__init__("Grid", children, props={"columns": _clean_value(columns), "gap": gap, **props})


class AstryxCenter(AstryxWidget):
    """Center child content in an Astryx container.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    axis : str, default 'both'
        Axis used for centering child content.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, children: ChildInput = None, *, axis: str = "both", **props: Any) -> None:
        super().__init__("Center", children, props={"axis": axis, **props})


class AstryxAspectRatio(AstryxWidget):
    """Constrain child content to a fixed aspect ratio.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    ratio : int | float, default '16 / 9'
        Aspect ratio as a numeric width divided by height value.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, children: ChildInput = None, *, ratio: int | float = 16 / 9, **props: Any) -> None:
        super().__init__("AspectRatio", children, props={"ratio": ratio, **props})


class AstryxCard(AstryxWidget):
    """Render an Astryx card container.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    variant : str, default 'default'
        Astryx visual variant.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, children: ChildInput = None, *, variant: str = "default", **props: Any) -> None:
        super().__init__("Card", children, variant=variant, props={"variant": variant, **props})


class AstryxClickableCard(AstryxWidget):
    """Render an Astryx card that behaves like an action target.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    label : str
        Visible or accessible label for the component.
    variant : str, default 'default'
        Astryx visual variant.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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
    """Render an Astryx card with a selected state.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    value : bool, default False
        Synchronized component value.
    label : str
        Visible or accessible label for the component.
    variant : str, default 'default'
        Astryx visual variant.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, children: ChildInput = None, value: bool = False, *, label: str, variant: str = "default", **props: Any) -> None:
        super().__init__("SelectableCard", children, label=label, value=value, variant=variant, props={"variant": variant, **props})


class AstryxSection(AstryxWidget):
    """Render an Astryx section container.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    variant : str, default 'section'
        Astryx visual variant.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, children: ChildInput = None, *, variant: str = "section", **props: Any) -> None:
        super().__init__("Section", children, variant=variant, props={"variant": variant, **props})


class AstryxDivider(AstryxWidget):
    """Render an Astryx divider.

    Parameters
    ----------
    orientation : str, default 'horizontal'
        Astryx component option.
    variant : str, default 'subtle'
        Astryx visual variant.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, *, orientation: str = "horizontal", variant: str = "subtle", **props: Any) -> None:
        super().__init__("Divider", variant=variant, props={"orientation": orientation, "variant": variant, **props})


class AstryxList(AstryxWidget):
    """Render an Astryx list from item records.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    header : str, default ''
        Optional header text or content.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, items: Iterable[Any], *, header: str = "", **props: Any) -> None:
        super().__init__("List", props={"items": _option_records(items), "header": header or None, **props})


class AstryxMetadataList(AstryxWidget):
    """Render label-value metadata rows.

    Parameters
    ----------
    items : Iterable[Mapping[str, Any]]
        Item records used by generated child components or static search sources.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, items: Iterable[Mapping[str, Any]], **props: Any) -> None:
        super().__init__("MetadataList", props={"items": _clean_value(list(items)), **props})


class AstryxBreadcrumbs(AstryxWidget):
    """Render Astryx breadcrumbs from item records.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, items: Iterable[Any], **props: Any) -> None:
        super().__init__("Breadcrumbs", props={"items": _option_records(items), **props})


class AstryxTabList(AstryxWidget):
    """Render an Astryx tab list.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    value : str
        Synchronized component value.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, items: Iterable[Any], value: str, **props: Any) -> None:
        super().__init__("TabList", value=value, props={"items": _option_records(items), **props})


class AstryxSegmentedControl(AstryxWidget):
    """Render a compact Astryx segmented control.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    value : str
        Synchronized component value.
    label : str
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, items: Iterable[Any], value: str, *, label: str, **props: Any) -> None:
        super().__init__("SegmentedControl", label=label, value=value, props={"items": _option_records(items), **props})


class AstryxRadioList(AstryxWidget):
    """Render a single-choice Astryx radio list.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    value : str
        Synchronized component value.
    label : str
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, items: Iterable[Any], value: str, *, label: str, **props: Any) -> None:
        super().__init__("RadioList", label=label, value=value, props={"items": _option_records(items), **props})


class AstryxCheckboxList(AstryxWidget):
    """Render a multi-choice Astryx checkbox list.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    value : Iterable[str], default ()
        Synchronized component value.
    label : str
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, items: Iterable[Any], value: Iterable[str] = (), *, label: str, **props: Any) -> None:
        super().__init__("CheckboxList", label=label, value=list(value), props={"items": _option_records(items), **props})


class AstryxButtonGroup(AstryxWidget):
    """Render an Astryx button group from item records.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    label : str
        Visible or accessible label for the component.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, items: Iterable[Any], *, label: str, callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None, **props: Any) -> None:
        super().__init__("ButtonGroup", label=label, callbacks=callbacks, props={"items": _option_records(items), "label": label, **props})


class AstryxAvatarGroup(AstryxWidget):
    """Render a compact group of Astryx avatars.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    overflow_count : int, default 0
        Number shown in the avatar-group overflow indicator.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, items: Iterable[Any], *, overflow_count: int = 0, **props: Any) -> None:
        super().__init__("AvatarGroup", props={"items": _option_records(items), "overflowCount": overflow_count, **props})


class AstryxCode(AstryxWidget):
    """Render inline code with Astryx styling.

    Parameters
    ----------
    code : str
        Astryx component option.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, code: str, **props: Any) -> None:
        super().__init__("Code", text=code, props=props)


class AstryxCitation(AstryxWidget):
    """Render a compact inline citation reference.

    Parameters
    ----------
    source : Mapping[str, Any]
        Citation source metadata.
    number : int, default 1
        Citation number.
    variant : str, default 'number'
        Astryx visual variant.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, source: Mapping[str, Any], *, number: int = 1, variant: str = "number", **props: Any) -> None:
        super().__init__("Citation", value=number, variant=variant, props={"source": _clean_value(source), "number": number, "variant": variant, **props})


class AstryxField(AstryxWidget):
    """Wrap a custom control with an Astryx field label.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    label : str
        Visible or accessible label for the component.
    input_id : str, default ''
        ID associated with the wrapped input element.
    description : str, default ''
        Supporting description text.
    status : Mapping[str, Any] | None
        Validation or status record displayed by Astryx.
    disabled : bool, default False
        Whether the component should render disabled.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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
        Astryx component option.
    type : str, default 'success'
        Astryx component option.
    variant : str, default 'detached'
        Astryx visual variant.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, message: str, *, type: str = "success", variant: str = "detached", **props: Any) -> None:
        super().__init__("FieldStatus", label=message, variant=type, props={"type": type, "message": message, "variant": variant, **props})


class AstryxFormLayout(AstryxWidget):
    """Arrange Astryx form controls with consistent spacing.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    direction : str, default 'vertical'
        Layout direction.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, children: ChildInput = None, *, direction: str = "vertical", **props: Any) -> None:
        super().__init__("FormLayout", children, props={"direction": direction, **props})


class AstryxInputGroup(AstryxWidget):
    """Group an input with prefix and suffix adornments.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    label : str
        Visible or accessible label for the component.
    prefix : str, default ''
        Text rendered before grouped input children.
    suffix : str, default ''
        Text rendered after grouped input children.
    disabled : bool, default False
        Whether the component should render disabled.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    trigger : str
        Trigger content used by disclosure or overlay components.
    default_open : bool, default True
        Initial uncontrolled open state.
    value : str, default ''
        Synchronized component value.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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
    items : Iterable[Mapping[str, Any]]
        Item records used by generated child components or static search sources.
    active_id : str, default ''
        Currently active outline item id.
    label : str, default 'Table of contents'
        Visible or accessible label for the component.
    density : str, default 'compact'
        Astryx density or spacing mode.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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
    items : Iterable[Mapping[str, Any]]
        Item records used by generated child components or static search sources.
    header : str, default ''
        Optional header text or content.
    density : str, default 'balanced'
        Astryx density or spacing mode.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, items: Iterable[Mapping[str, Any]], *, header: str = "", density: str = "balanced", **props: Any) -> None:
        super().__init__("TreeList", props={"items": _clean_value(list(items)), "header": header or None, "density": density, **props})


class AstryxToolbar(AstryxWidget):
    """Render an Astryx toolbar with optional slots.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    label : str
        Visible or accessible label for the component.
    size : str, default 'sm'
        Astryx component option.
    gap : int | float, default 1
        Astryx spacing step between children.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, children: ChildInput = None, *, label: str, size: str = "sm", gap: int | float = 1, **props: Any) -> None:
        super().__init__("Toolbar", children, label=label, props={"label": label, "size": size, "gap": gap, **props})


class AstryxTooltip(AstryxWidget):
    """Attach a tooltip to notebook content.

    Parameters
    ----------
    content : str | ChildInput
        Overlay or tooltip content.
    trigger : ChildInput
        Trigger content used by disclosure or overlay components.
    label : str, default ''
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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
    content : str | ChildInput
        Overlay or tooltip content.
    trigger : ChildInput
        Trigger content used by disclosure or overlay components.
    label : str, default ''
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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
    content : str | ChildInput
        Overlay or tooltip content.
    trigger : ChildInput
        Trigger content used by disclosure or overlay components.
    label : str
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    label : str
        Visible or accessible label for the component.
    variant : str, default 'secondary'
        Astryx visual variant.
    disabled : bool, default False
        Whether the component should render disabled.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    label : str, default 'More options'
        Visible or accessible label for the component.
    variant : str, default 'ghost'
        Astryx visual variant.
    disabled : bool, default False
        Whether the component should render disabled.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked for frontend activations.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

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
    value : str | Mapping[str, str] | None
        Synchronized component value.
    mode : str, default 'single'
        Component mode.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, value: str | Mapping[str, str] | None = None, *, mode: str = "single", **props: Any) -> None:
        super().__init__("Calendar", value=value, props={"mode": mode, **props})


class AstryxFileInput(AstryxWidget):
    """Render an Astryx file input.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    value : Any
        Synchronized component value.
    multiple : bool, default False
        Whether multiple files can be selected.
    disabled : bool, default False
        Whether the component should render disabled.
    **props : Any
        Additional Astryx component props serialized to the frontend.

    Notes
    -----
    The synchronized value contains file metadata only; file bytes are not sent to Python."""

    def __init__(self, *, label: str, value: Any = None, multiple: bool = False, disabled: bool = False, **props: Any) -> None:
        super().__init__("FileInput", label=label, value=value, disabled=disabled, props={"label": label, "isMultiple": multiple, **props})


class AstryxTypeahead(AstryxWidget):
    """Render a notebook-safe Astryx typeahead with a static search source.

    Parameters
    ----------
    items : Iterable[Any] | Mapping[str, Any]
        Searchable items. Mappings, pairs, strings, and dictionaries are
        normalized into ``{"id": ..., "label": ...}`` records.
    value : str | None
        Selected item id synchronized back to Python. Use ``None`` for no
        initial selection.
    label : str
        Accessible field label.
    disabled : bool, default False
        Whether the input should render disabled.
    **props : Any
        Additional Astryx Typeahead props serialized to the frontend.

    Notes
    -----
    The frontend receives an Astryx ``createStaticSource`` backed by ``items``.
    Query text and open-state changes are emitted as widget messages, while the
    selected item id is stored in ``value``.
    """

    def __init__(self, items: Iterable[Any] | Mapping[str, Any], value: str | None = None, *, label: str, disabled: bool = False, **props: Any) -> None:
        super().__init__("Typeahead", label=label, value=value, disabled=disabled, props={"items": _search_records(items), "label": label, **props})


class AstryxTokenizer(AstryxWidget):
    """Render a notebook-safe Astryx tokenizer with a static search source.

    Parameters
    ----------
    items : Iterable[Any] | Mapping[str, Any]
        Searchable items. Mappings, pairs, strings, and dictionaries are
        normalized into ``{"id": ..., "label": ...}`` records.
    value : Iterable[str], default ()
        Selected item ids synchronized back to Python.
    label : str
        Accessible field label.
    disabled : bool, default False
        Whether the input and token interactions should render disabled.
    **props : Any
        Additional Astryx Tokenizer props serialized to the frontend.

    Notes
    -----
    The wrapper stores selected ids in ``value`` rather than complete item
    records so notebook state remains compact and JSON-safe.
    """

    def __init__(self, items: Iterable[Any] | Mapping[str, Any], value: Iterable[str] = (), *, label: str, disabled: bool = False, **props: Any) -> None:
        super().__init__("Tokenizer", label=label, value=list(value), disabled=disabled, props={"items": _search_records(items), "label": label, **props})


class AstryxCommandPalette(AstryxWidget):
    """Render an inline Astryx command palette for notebook output areas.

    Parameters
    ----------
    items : Iterable[Any] | Mapping[str, Any]
        Command records. Mappings, pairs, strings, and dictionaries are
        normalized into ``{"id": ..., "label": ...}`` records.
    value : str | None
        Selected command id synchronized back to Python.
    label : str, default 'Command palette'
        Accessible dialog label.
    **props : Any
        Additional Astryx CommandPalette props serialized to the frontend.

    Notes
    -----
    The palette renders inline and open by default so it remains contained in a
    Jupyter output area instead of creating a page-level modal overlay.
    """

    def __init__(self, items: Iterable[Any] | Mapping[str, Any], value: str | None = None, *, label: str = "Command palette", **props: Any) -> None:
        super().__init__("CommandPalette", label=label, value=value, props={"items": _search_records(items), "label": label, "isInline": True, **props})


class AstryxDialog(AstryxWidget):
    """Render Astryx dialog content inline in notebook output.

    Parameters
    ----------
    children : ChildInput
        Dialog body content. Pass a widget, a sequence of widgets, or a mapping
        of slot names to widgets.
    open : bool, default True
        Initial open state synchronized through ``value``.
    inline : bool, default True
        Whether dialog content renders inline instead of using native modal
        behavior.
    **props : Any
        Additional Astryx Dialog props serialized to the frontend.

    Notes
    -----
    The wrapper defaults to inline rendering to avoid modal focus-management
    conflicts inside Jupyter output areas. Set ``inline=False`` only when the
    surrounding notebook environment can safely host modal dialogs.
    """

    def __init__(self, children: ChildInput = None, *, open: bool = True, inline: bool = True, **props: Any) -> None:
        super().__init__("Dialog", children, value=open, props={"isInline": inline, **props})


class AstryxAlertDialog(AstryxWidget):
    """Render an inline Astryx alert dialog for confirmations.

    Parameters
    ----------
    title : str
        Dialog title linked to the alert for accessibility.
    description : str
        Consequence or confirmation text linked to the alert for accessibility.
    action_label : str
        Primary action button label.
    cancel_label : str, default 'Cancel'
        Cancel button label.
    open : bool, default True
        Initial open state synchronized through ``value``.
    inline : bool, default True
        Whether dialog content renders inline instead of using native modal
        behavior.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None
        Python callbacks invoked when the primary action is activated.
    **props : Any
        Additional Astryx AlertDialog props serialized to the frontend.

    Notes
    -----
    The wrapper defaults to inline rendering to avoid modal focus-management
    conflicts inside Jupyter output areas. The primary action emits a click
    message with ``action="confirm"``.
    """

    def __init__(
        self,
        title: str,
        description: str,
        *,
        action_label: str,
        cancel_label: str = "Cancel",
        open: bool = True,
        inline: bool = True,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "AlertDialog",
            label=title,
            text=description,
            value=open,
            callbacks=callbacks,
            props={
                "title": title,
                "description": description,
                "actionLabel": action_label,
                "cancelLabel": cancel_label,
                "isInline": inline,
                **props,
            },
        )


# TODO(astryx): Follow up with asynchronous Python-backed search sources for
# Typeahead, Tokenizer, and CommandPalette if notebooks need server-side search,
# and evaluate non-inline Dialog/AlertDialog behavior once JupyterLab output
# focus and layer interactions are well understood.


class AstryxTable(AstryxWidget):
    """Render a data-driven Astryx table for notebook use.

    Parameters
    ----------
    rows : Iterable[Any], default ()
        Rows or records rendered by the component.
    columns : Iterable[Any] | Mapping[str, Any] | None
        Grid or table column definition.
    row_key : str | None, default 'id'
        Row id field. Use ``None`` to generate notebook-local row ids.
    selected : Iterable[Any], default ()
        Initially selected row ids.
    selects : str, default ''
        Selection mode. Use ``""``, ``"single"``, or ``"multiple"``.
    sortable : bool, default False
        Whether table columns should be sortable by default.
    sort_key : str, default ''
        Initially sorted table column key.
    sort_direction : str, default ''
        Initial sort direction, such as ``"asc"`` or ``"desc"``.
    select_all_label : str, default 'Select all rows'
        Accessible label for the select-all checkbox.
    width : int | float | str | None
        CSS width. Numbers are normalized by anylumino where supported.
    height : int | float | str | None
        CSS height. Numbers are normalized by anylumino where supported.
    **props : Any
        Additional Astryx component props serialized to the frontend.

    Notes
    -----
    Row checkbox selection is optional. Leave ``selects`` empty for no checkbox column, use ``"single"`` or ``"multiple"`` to enable selection."""

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

    Parameters
    ----------
    title : str
        Dialog or empty-state title.
    description : str, default ''
        Supporting description text.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, title: str, *, description: str = "", **props: Any) -> None:
        super().__init__("EmptyState", props={"title": title, "description": description, **props})


class AstryxBanner(AstryxWidget):
    """Render an Astryx banner for prominent status messages.

    Parameters
    ----------
    title : str
        Dialog or empty-state title.
    status : str, default 'info'
        Validation or status record displayed by Astryx.
    description : str, default ''
        Supporting description text.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, title: str, *, status: str = "info", description: str = "", **props: Any) -> None:
        super().__init__("Banner", label=title, props={"title": title, "status": status, "description": description, **props})


class AstryxStatusDot(AstryxWidget):
    """Render an inline Astryx status indicator.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    variant : str, default 'neutral'
        Astryx visual variant.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, label: str, *, variant: str = "neutral", **props: Any) -> None:
        super().__init__("StatusDot", label=label, variant=variant, props=props)


class AstryxProgressBar(AstryxWidget):
    """Render an Astryx progress bar.

    Parameters
    ----------
    value : int | float, default 0
        Synchronized component value.
    label : str
        Visible or accessible label for the component.
    variant : str, default 'accent'
        Astryx visual variant.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, value: int | float = 0, *, label: str, variant: str = "accent", **props: Any) -> None:
        super().__init__("ProgressBar", label=label, value=value, variant=variant, props=props)


class AstryxSpinner(AstryxWidget):
    """Render an Astryx loading spinner.

    Parameters
    ----------
    label : str, default 'Loading'
        Visible or accessible label for the component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, *, label: str = "Loading", **props: Any) -> None:
        super().__init__("Spinner", label=label, props={"label": label, **props})


class AstryxSkeleton(AstryxWidget):
    """Render an Astryx skeleton placeholder.

    Parameters
    ----------
    width : int | str, default '100%'
        CSS width. Numbers are normalized by anylumino where supported.
    height : int | str, default 16
        CSS height. Numbers are normalized by anylumino where supported.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, *, width: int | str = "100%", height: int | str = 16, **props: Any) -> None:
        super().__init__("Skeleton", props={"width": width, "height": height, **props})


class AstryxToken(AstryxWidget):
    """Render an Astryx token or chip.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    color : str, default 'default'
        Astryx component option.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, label: str, *, color: str = "default", **props: Any) -> None:
        super().__init__("Token", label=label, props={"color": color, **props})


class AstryxKbd(AstryxWidget):
    """Render keyboard shortcut text with Astryx styling.

    Parameters
    ----------
    keys : str
        Keyboard shortcut text.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, keys: str, **props: Any) -> None:
        super().__init__("Kbd", props={"keys": keys, **props})


class AstryxLink(AstryxWidget):
    """Render an Astryx text link.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    href : str, default ''
        Link destination URL.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, label: str, *, href: str = "", **props: Any) -> None:
        super().__init__("Link", text=label, label=label, props={"href": href or None, **props})


class AstryxAvatar(AstryxWidget):
    """Render an Astryx avatar.

    Parameters
    ----------
    name : str
        Astryx component option.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, name: str, **props: Any) -> None:
        super().__init__("Avatar", label=name, props={"name": name, **props})


class AstryxIcon(AstryxWidget):
    """Render an Astryx icon by name.

    Parameters
    ----------
    icon : str
        Astryx icon name.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, icon: str, **props: Any) -> None:
        super().__init__("Icon", text=icon, icon=icon, props={"icon": icon, **props})


class AstryxThumbnail(AstryxWidget):
    """Render an Astryx thumbnail image or placeholder.

    Parameters
    ----------
    label : str, default ''
        Visible or accessible label for the component.
    src : str, default ''
        Image or media source URL.
    alt : str, default ''
        Accessible alternative text.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, *, label: str = "", src: str = "", alt: str = "", **props: Any) -> None:
        super().__init__("Thumbnail", label=label, props={"src": src or None, "alt": alt or label, "label": label, **props})


class AstryxCodeBlock(AstryxWidget):
    """Render syntax-highlighted code with Astryx styling.

    Parameters
    ----------
    code : str
        Astryx component option.
    language : str, default 'python'
        Code language used for syntax highlighting.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, code: str, *, language: str = "python", **props: Any) -> None:
        super().__init__("CodeBlock", props={"code": code, "language": language, **props})


class AstryxMarkdown(AstryxWidget):
    """Render Markdown content through Astryx.

    Parameters
    ----------
    text : str
        Text content synchronized to the frontend component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, text: str, **props: Any) -> None:
        super().__init__("Markdown", text=text, props=props)


class AstryxBlockquote(AstryxWidget):
    """Render quoted text with Astryx blockquote styling.

    Parameters
    ----------
    text : str
        Text content synchronized to the frontend component.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, text: str, **props: Any) -> None:
        super().__init__("Blockquote", text=text, props=props)


class AstryxTimestamp(AstryxWidget):
    """Render a timestamp value with Astryx formatting.

    Parameters
    ----------
    value : str | int | float
        Synchronized component value.
    **props : Any
        Additional Astryx component props serialized to the frontend."""

    def __init__(self, value: str | int | float, **props: Any) -> None:
        super().__init__("Timestamp", value=value, props=props)


__all__ = [
    "AstryxAspectRatio",
    "AstryxAlertDialog",
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
    "AstryxCommandPalette",
    "AstryxComponent",
    "AstryxCollapsible",
    "AstryxDropdownMenu",
    "AstryxDateInput",
    "AstryxDateRangeInput",
    "AstryxDateTimeInput",
    "AstryxDialog",
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
    "AstryxTheme",
    "AstryxThumbnail",
    "AstryxTimeInput",
    "AstryxTimestamp",
    "AstryxToggleButton",
    "AstryxToken",
    "AstryxTokenizer",
    "AstryxToolbar",
    "AstryxTooltip",
    "AstryxTreeList",
    "AstryxTypeahead",
    "AstryxWidget",
    "AstryxBrand",
]
