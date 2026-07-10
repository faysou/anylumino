"""Core Astryx widget abstractions and theme support."""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from os import PathLike
from typing import Any

import traitlets as t

from ..common import json_value as _json_value
from ..common import static_asset
from ..components import ComponentWidget
from ..layout import ChildInput


_ASTRYX_THEME_MODES = ("light", "dark", "system")
_ASTRYX_COMPONENT_NAMES = {
    "AlertDialog",
    "AspectRatio",
    "Avatar",
    "AvatarGroup",
    "Badge",
    "Banner",
    "Blockquote",
    "Breadcrumbs",
    "Button",
    "ButtonGroup",
    "Calendar",
    "Card",
    "Center",
    "CheckboxInput",
    "CheckboxList",
    "Citation",
    "ClickableCard",
    "Code",
    "CodeBlock",
    "Collapsible",
    "CommandPalette",
    "DateInput",
    "DateRangeInput",
    "DateTimeInput",
    "Dialog",
    "Divider",
    "DropdownMenu",
    "EmptyState",
    "Field",
    "FieldStatus",
    "FileInput",
    "FormLayout",
    "Grid",
    "Heading",
    "HoverCard",
    "Icon",
    "IconButton",
    "InputGroup",
    "Item",
    "Kbd",
    "Link",
    "List",
    "Lightbox",
    "Markdown",
    "MetadataList",
    "MoreMenu",
    "MultiSelector",
    "NumberInput",
    "Outline",
    "Overlay",
    "Pagination",
    "Popover",
    "ProgressBar",
    "RadioList",
    "Section",
    "SegmentedControl",
    "SelectableCard",
    "Selector",
    "Skeleton",
    "Slider",
    "Spinner",
    "Stack",
    "StatusDot",
    "Switch",
    "Table",
    "TabList",
    "Text",
    "TextArea",
    "TextInput",
    "Thumbnail",
    "TimeInput",
    "Timestamp",
    "ToggleButton",
    "ToggleButtonGroup",
    "Token",
    "Tokenizer",
    "Toolbar",
    "Tooltip",
    "TreeList",
    "Typeahead",
}


def _clean_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _clean_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean_value(item) for item in value]
    return _json_value(value)


def _clean_props(props: Mapping[str, Any] | None) -> dict[str, Any]:
    return {str(key): _clean_value(value) for key, value in dict(props or {}).items()}


def _named_props(
    props: Mapping[str, Any] | None = None, **values: Any
) -> dict[str, Any]:
    normalized = dict(props or {})
    normalized.update(
        {name: value for name, value in values.items() if value is not None}
    )
    return normalized


def _clean_theme_token_name(name: object) -> str:
    token_name = str(name)
    return token_name if token_name.startswith("--") else f"--{token_name}"


def _clean_theme_css(css: str | PathLike[str] | None) -> str:
    if css is None:
        return ""
    if isinstance(css, PathLike):
        with open(css, encoding="utf-8") as css_file:
            return css_file.read()
    return str(css)


def _clean_astryx_theme(theme: Mapping[str, Any] | None) -> dict[str, Any]:
    if not theme:
        return {}
    if theme.get("built") or theme.get("__built"):
        tokens = theme.get("tokens", {})
        return {
            "name": str(theme.get("name", "neutral")),
            "built": True,
            "tokens": {
                _clean_theme_token_name(key): _clean_value(value)
                for key, value in dict(tokens or {}).items()
            },
            "css": _clean_theme_css(theme.get("css")),
            "components": _clean_value(theme.get("components", {})),
        }
    if "tokens" in theme:
        tokens = theme.get("tokens")
    else:
        tokens = {key: value for key, value in theme.items() if key != "name"}
    return {
        "name": str(theme.get("name", "anylumino-brand")),
        "tokens": {
            _clean_theme_token_name(key): _clean_value(value)
            for key, value in dict(tokens or {}).items()
        },
    }


def _clean_brand(brand: Mapping[str, Any] | None) -> dict[str, Any]:
    return _clean_astryx_theme(brand)


def _clean_theme_mode(mode: str) -> str:
    if mode not in _ASTRYX_THEME_MODES:
        expected = ", ".join(_ASTRYX_THEME_MODES)
        raise ValueError(f"theme mode must be one of: {expected}")
    return mode


def _option_records(options: Iterable[Any] | Mapping[str, Any]) -> list[Any]:
    if isinstance(options, Mapping):
        return [
            {"label": str(label), "value": str(value)}
            for label, value in options.items()
        ]

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


def _table_columns(
    columns: Iterable[Any] | Mapping[str, Any] | None, rows: Iterable[Any]
) -> list[Any]:
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
        return [
            {
                "key": str(key),
                "header": str(header),
                "width": {"kind": "proportional", "value": 1},
            }
            for key, header in columns.items()
        ]

    normalized = []
    for index, column in enumerate(columns):
        if isinstance(column, Mapping):
            item = _clean_value(column)
            item["key"] = str(
                item.get("key", item.get("value", _table_column_key(index)))
            )
            item["header"] = str(item.get("header", item.get("label", item["key"])))
            if "width" not in item:
                item["width"] = {"kind": "proportional", "value": 1}
            else:
                item["width"] = _astryx_table_width(item["width"])
            normalized.append(item)
        elif isinstance(column, (list, tuple)) and len(column) == 2:
            header, key = column
            normalized.append(
                {
                    "key": str(key),
                    "header": str(header),
                    "width": {"kind": "proportional", "value": 1},
                }
            )
        else:
            normalized.append(
                {
                    "key": str(column),
                    "header": str(column),
                    "width": {"kind": "proportional", "value": 1},
                }
            )
    return normalized


def _table_rows(
    rows: Iterable[Any], columns: list[dict[str, Any]], row_key: str
) -> list[dict[str, Any]]:
    normalized = []
    for index, row in enumerate(rows):
        if isinstance(row, Mapping):
            item = {
                column["key"]: _clean_value(row.get(column["key"], ""))
                for column in columns
            }
            item[row_key] = _clean_value(row.get(row_key, index))
        elif isinstance(row, (list, tuple)):
            item = {
                column["key"]: _clean_value(row[column_index])
                if column_index < len(row)
                else ""
                for column_index, column in enumerate(columns)
            }
            item[row_key] = str(index)
        else:
            item = (
                {columns[0]["key"]: _clean_value(row)}
                if columns
                else {"value": _clean_value(row)}
            )
            item[row_key] = str(index)
        normalized.append(item)
    return normalized


class Widget(ComponentWidget):
    """Base anywidget for Astryx-backed components.

    Parameters
    ----------
    component_name : str, default 'Stack'
        Frontend Astryx component name registered in the anylumino bridge.
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    props : Mapping[str, Any] | None
        Additional JSON-safe props for the selected Astryx component.
        Use this for component options that are not modeled as widget traits.
        anylumino manages widget composition, value synchronization, callbacks, and brand/theme
        traits separately.
        Upstream React-only values such as functions, refs, and React nodes are not serializable
        from Python.
        See the Astryx docs for the selected component page, for example <https://astryx.atmeta.com/components/Blockquote>.
    text : str, default ''
        Text content synchronized to the frontend.
    label : str, default ''
        Visible or accessible component label.
    value : Any, default None
        Synchronized component value.
    disabled : bool, default False
        Whether the component is disabled.
    variant : str, default ''
        Astryx visual variant.
    brand : Mapping[str, Any] | None, default None
        Runtime or built Astryx theme descriptor.
    color_mode : str, default 'light'
        Astryx ``Theme`` mode. Use ``"light"``, ``"dark"``, or ``"system"``.
    search : Callable[[str], Iterable[Any]] | None, default None
        Optional Python-backed search callback.
    callbacks : Iterable[Callable[[ComponentWidget], None]] | None, default None
        Python activation callbacks.
    action_callbacks : Iterable[Callable[[ComponentWidget, Any], None]] | None, default None
        Python callbacks receiving named action values.
    open : bool | None, default None
        Optional controlled open state.
    width : int | float | str | None, default None
        Component host width.
    height : int | float | str | None, default None
        Component host height.
    """

    _esm = static_asset("astryx/astryx_widget.bundle.js")
    _css = static_asset("astryx/astryx_widget.bundle.css")

    component_family = t.Unicode("astryx").tag(sync=True)
    component_name = t.Unicode("Stack").tag(sync=True)
    props = t.Dict(default_value={}).tag(sync=True)
    color_mode = t.Enum(_ASTRYX_THEME_MODES, default_value="light").tag(sync=True)
    theme = t.Unicode("neutral").tag(sync=True)
    brand = t.Dict(default_value={}).tag(sync=True)
    search_mode = t.Unicode("static").tag(sync=True)

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
        color_mode: str = "light",
        search: Callable[[str], Iterable[Any]] | None = None,
        callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None,
        action_callbacks: Iterable[Callable[[ComponentWidget, Any], None]]
        | None = None,
        open: bool | None = None,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        **kwargs: Any,
    ) -> None:
        raw_props = dict(props or {})
        brand = raw_props.pop("brand", brand)
        color_mode = str(raw_props.pop("color_mode", color_mode))
        callbacks = raw_props.pop("callbacks", callbacks)
        action_callbacks = raw_props.pop("action_callbacks", action_callbacks)
        if width is None:
            width = raw_props.get("width")
        if height is None:
            height = raw_props.get("height")
        if not disabled and "isDisabled" in raw_props:
            disabled = bool(raw_props["isDisabled"])
        if open is None and "isOpen" in raw_props:
            open = bool(raw_props["isOpen"])
        self._search_callback = search
        super().__init__(
            children,
            component_kind=component_name,
            component_name=component_name,
            props=_clean_props(raw_props),
            text=text,
            label=label,
            value=_clean_value(value),
            disabled=disabled,
            variant=variant,
            brand=_clean_brand(brand),
            color_mode=_clean_theme_mode(color_mode),
            search_mode="python" if search is not None else "static",
            callbacks=callbacks,
            action_callbacks=action_callbacks,
            is_open=bool(open),
            width=width,
            height=height,
            **kwargs,
        )

    def apply_brand(
        self, brand: Mapping[str, Any] | None, *, color_mode: str | None = None
    ) -> None:
        """Apply a reusable Astryx brand identity to this widget subtree."""
        self.brand = _clean_brand(brand)
        if color_mode is not None:
            self.color_mode = _clean_theme_mode(color_mode)
        for child in self.widgets:
            if isinstance(child, Widget):
                child.apply_brand(self.brand, color_mode=color_mode)

    def _handle_frontend_message(
        self, widget: object, content: dict[str, Any], buffers: object
    ) -> None:
        if content.get("type") != "search":
            super()._handle_frontend_message(widget, content, buffers)
            return

        request_id = str(content.get("request_id", ""))
        query = str(content.get("query", ""))
        callback = self._search_callback
        if callback is None:
            self.send(
                {
                    "type": "search-results",
                    "request_id": request_id,
                    "query": query,
                    "items": [],
                }
            )
            return

        try:
            items = _search_records(callback(query))
        except Exception as exc:  # pragma: no cover - frontend resilience path
            self.send(
                {
                    "type": "search-results",
                    "request_id": request_id,
                    "query": query,
                    "items": [],
                    "error": str(exc),
                },
            )
            return

        self.send(
            {
                "type": "search-results",
                "request_id": request_id,
                "query": query,
                "items": items,
            }
        )


def Brand(name: str = "anylumino-brand", **tokens: Any) -> dict[str, Any]:
    """Create a reusable Astryx runtime theme token mapping.

    Parameters
    ----------
    name : str, default "anylumino-brand"
        Name assigned to the runtime Astryx theme.
    **tokens : Any
        Astryx ``defineTheme()`` design tokens. Names may include or omit the
        leading ``"--"`` and are normalized to CSS custom property names.
        Values may be strings or two-item ``(light, dark)`` tuples. Common
        keys include ``--color-accent``, ``--color-background-surface``,
        ``--color-background-body``, ``--color-text-primary``,
        ``--color-text-secondary``, ``--radius-container``, and
        ``--spacing-1`` through ``--spacing-6``.

    Returns
    -------
    dict
        JSON-safe runtime theme record that can be passed to
        :class:`Theme` or :meth:`Widget.apply_brand`.

    Notes
    -----
    The frontend bridge passes this record to Astryx ``defineTheme()`` and
    renders widgets inside Astryx ``Theme``. Use :func:`BuiltTheme`
    when you already have CSS generated by ``npx astryx theme build``.
    """
    return _clean_brand({"name": name, "tokens": tokens})


def BuiltTheme(
    name: str = "neutral",
    *,
    css: str | PathLike[str] | None = None,
    tokens: Mapping[str, Any] | None = None,
    components: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a JSON-safe descriptor for a precompiled Astryx theme.

    Parameters
    ----------
    name : str, default 'neutral'
        Astryx theme name used by the generated CSS ``data-astryx-theme``
        selectors. This must match the ``name`` in the TypeScript theme passed
        to ``npx astryx theme build``.
    css : str | os.PathLike[str] | None, default None
        Generated theme CSS content or a path to the generated CSS file. Pass
        ``None`` for built themes whose CSS is already bundled by AnyLumino,
        such as the default neutral theme.
    tokens : Mapping[str, Any] | None, default None
        Optional resolved token map from the built theme object. Token names may
        include or omit the leading ``"--"``. The CSS is what styles widgets;
        tokens are retained for Astryx hooks and debugging.
    components : Mapping[str, Any] | None, default None
        Optional built component override metadata from the Astryx theme object.

    Returns
    -------
    dict
        JSON-safe precompiled theme descriptor that can be passed to
        :class:`Theme`, :class:`Widget`, or
        :meth:`Widget.apply_brand`.

    Notes
    -----
    Built theme descriptors set ``__built`` in the frontend so Astryx ``Theme``
    does not perform runtime style injection. When ``css`` is supplied,
    AnyLumino injects that generated CSS into the notebook page and reuses it
    across widgets with the same content.
    """
    return _clean_astryx_theme(
        {
            "name": name,
            "built": True,
            "css": css,
            "tokens": tokens or {},
            "components": components or {},
        },
    )


class Component(Widget):
    """Render a registered Astryx component by name.

    Parameters
    ----------
    component_name : str
        Frontend Astryx component name registered in the anylumino bridge.
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    props : Mapping[str, Any] | None
        Additional JSON-safe props for the selected Astryx component.
        Unsafe React keys such as ``children``, ``dangerouslySetInnerHTML``, ``ref``, and ``key``
        are filtered by the frontend bridge. Component data props such as ``items`` are preserved.
        See the Astryx docs for the selected component page, for example <https://astryx.atmeta.com/components/Blockquote>.
    text : str, default ''
        Text content synchronized to the frontend.
    label : str, default ''
        Visible or accessible component label.
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
        if component_name not in _ASTRYX_COMPONENT_NAMES:
            registered = ", ".join(sorted(_ASTRYX_COMPONENT_NAMES))
            raise ValueError(
                f"unknown Astryx component {component_name!r}; registered components: {registered}"
            )
        super().__init__(
            component_name,
            children,
            props=props,
            text=text,
            label=label,
            **kwargs,
        )


class Theme(Widget):
    """Apply a reusable Astryx theme to child widgets.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    brand : Mapping[str, Any] | None
        Reusable Astryx theme descriptor created by :func:`Brand` or
        :func:`BuiltTheme`.
    color_mode : str, default 'light'
        Astryx ``Theme`` mode for this component or subtree. Use ``"light"``,
        ``"dark"``, or ``"system"``.
    mode : str | None
        Alias for ``color_mode`` matching the Astryx ``Theme`` prop name. When
        provided, it takes precedence over ``color_mode``.
    direction : str, default 'vertical'
        Layout direction.
    gap : int | float, default 2
        Astryx spacing step between children.
    align : str | None, default None
        Cross-axis alignment.
    justify : str | None, default None
        Main-axis alignment.
    width : int | float | str | None, default None
        Theme container width.
    height : int | float | str | None, default None
        Theme container height.
    padding : int | float | None, default None
        Inner padding using the Astryx spacing scale.
    wrap : str | None, default None
        Stack wrapping behavior.
    scrollable : bool | None, default None
        Whether overflow should scroll.
    **props : Any
        JSON-safe Stack props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Stack props forwarded to Astryx.

    Supported Astryx props include:

    - ``direction`` ('horizontal' or 'vertical'; default 'vertical'): Direction of the stack layout.
    - ``hAlign`` (StackAlignment): Horizontal alignment. With horizontal direction it controls the
      main axis; with vertical direction it controls the cross axis.
    - ``vAlign`` (StackAlignment): Vertical alignment. With horizontal direction it controls the
      cross axis; with vertical direction it controls the main axis.
    - ``justify`` (StackMainAlignment): Main-axis alignment alias resolved from direction, mirroring
      CSS justify-content.
    - ``align`` (StackCrossAlignment): Cross-axis alignment alias resolved from direction, mirroring
      CSS align-items.
    - ``width`` (number or string): Container width. Numbers are pixels; strings are used as CSS
      values.
    - ``height`` (number or string): Container height. Numbers are pixels; strings are used as CSS
      values.
    - ``gap`` (spacing step): Spacing between items. Accepts Astryx spacing steps such as 0, 0.5, 1,
      2, 3, 4, 6, 8, and 10.
    - ``padding`` (spacing step): Inner padding on all sides using the spacing scale.
    - ``paddingInline`` (spacing step): Horizontal padding override; takes precedence over padding
      on the inline axis.
    - ``paddingBlock`` (spacing step): Vertical padding override; takes precedence over padding on
      the block axis.
    - ``isScrollable`` (boolean; default false): Enables scrollable overflow on the stack container.
    - ``wrap`` ('nowrap' or 'wrap' or 'wrap-reverse'; default 'nowrap'): Controls whether items wrap
      onto additional lines.
    - ``as`` (ElementType; default div): Element type to render for the root element.
    - ``xstyle`` (StyleXStyles): StyleX styles created with stylex.create().
    - ``className`` (string): CSS class names appended to the root element.
    - ``style`` (CSSProperties): Inline styles applied after StyleX styles.
    - ``children`` (ReactNode): Content rendered inside the stack.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Stack>.

    Notes
    -----
    This wrapper propagates theme descriptors to nested Astryx child widgets
    because each anywidget renders in its own frontend root."""

    def __init__(
        self,
        children: ChildInput = None,
        *,
        brand: Mapping[str, Any] | None = None,
        color_mode: str = "light",
        mode: str | None = None,
        direction: str = "vertical",
        gap: int | float = 2,
        align: str | None = None,
        justify: str | None = None,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        padding: int | float | None = None,
        wrap: str | None = None,
        scrollable: bool | None = None,
        **props: Any,
    ) -> None:
        effective_mode = _clean_theme_mode(mode or color_mode)
        super().__init__(
            "Stack",
            children,
            props=_named_props(
                props,
                direction=direction,
                gap=gap,
                align=align,
                justify=justify,
                width=width,
                height=height,
                padding=padding,
                wrap=wrap,
                isScrollable=scrollable,
            ),
            brand=brand,
            color_mode=effective_mode,
            width=width,
            height=height,
        )
        self.apply_brand(brand, color_mode=effective_mode)
