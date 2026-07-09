from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from os import PathLike
from typing import Any

import traitlets as t

from .common import json_value as _json_value
from .common import static_asset
from .components import ComponentWidget
from .layout import ChildInput


_ASTRYX_THEME_MODES = ("light", "dark", "system")


def _clean_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _clean_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean_value(item) for item in value]
    return _json_value(value)


def _clean_props(props: Mapping[str, Any] | None) -> dict[str, Any]:
    return {str(key): _clean_value(value) for key, value in dict(props or {}).items()}


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
            "tokens": {_clean_theme_token_name(key): _clean_value(value) for key, value in dict(tokens or {}).items()},
            "css": _clean_theme_css(theme.get("css")),
            "components": _clean_value(theme.get("components", {})),
        }
    if "tokens" in theme:
        tokens = theme.get("tokens")
    else:
        tokens = {key: value for key, value in theme.items() if key != "name"}
    return {
        "name": str(theme.get("name", "anylumino-brand")),
        "tokens": {_clean_theme_token_name(key): _clean_value(value) for key, value in dict(tokens or {}).items()},
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
    color_mode : str, default 'light'
        Astryx ``Theme`` mode. Use ``"light"``, ``"dark"``, or ``"system"``.
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
        **kwargs: Any,
    ) -> None:
        self._search_callback = search
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
            color_mode=_clean_theme_mode(color_mode),
            search_mode="python" if search is not None else "static",
            callbacks=callbacks,
            **kwargs,
        )

    def apply_brand(self, brand: Mapping[str, Any] | None, *, color_mode: str | None = None) -> None:
        """Apply a reusable Astryx brand identity to this widget subtree."""
        self.brand = _clean_brand(brand)
        if color_mode is not None:
            self.color_mode = _clean_theme_mode(color_mode)
        for child in self.widgets:
            if isinstance(child, Widget):
                child.apply_brand(self.brand, color_mode=color_mode)

    def _handle_frontend_message(self, widget: object, content: dict[str, Any], buffers: object) -> None:
        if content.get("type") != "search":
            super()._handle_frontend_message(widget, content, buffers)
            return

        request_id = str(content.get("request_id", ""))
        query = str(content.get("query", ""))
        callback = self._search_callback
        if callback is None:
            self.send({"type": "search-results", "request_id": request_id, "query": query, "items": []})
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

        self.send({"type": "search-results", "request_id": request_id, "query": query, "items": items})


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
        Reserved keys such as children, dangerouslySetInnerHTML, ref, key, items, tabs,
        segments, and metadata are filtered by the frontend bridge.
        See the Astryx docs for the selected component page, for example <https://astryx.atmeta.com/components/Blockquote>.
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
        **props: Any,
    ) -> None:
        effective_mode = _clean_theme_mode(mode or color_mode)
        super().__init__(
            "Stack",
            children,
            props={"direction": direction, "gap": gap, **props},
            brand=brand,
            color_mode=effective_mode,
        )
        self.apply_brand(brand, color_mode=effective_mode)


class Text(Widget):
    """Render themed Astryx body text.

    Parameters
    ----------
    text : str
        Text content synchronized to the frontend component.
    props : Mapping[str, Any] | None
        JSON-safe Text props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Text props forwarded to Astryx.

    Supported Astryx props include:

    - ``type`` ('body' or 'large' or 'label' or 'supporting' or 'code' or 'display-1' or 'display-2'
      or 'display-3'): Semantic text type. Determines size, weight, and line-height from the
      theme. Note: this prop is called 'type', not 'variant'.
    - ``children`` (ReactNode; required): Text content.
    - ``size`` ('4xs' or '3xs' or '2xs' or 'xsm' or 'sm' or 'base' or 'lg' or 'xl' or '2xl' or '3xl'
      or '4xl'): Explicit font size override. Overrides the size from 'type' but preserves other
      type properties. Prefer using 'type' alone.
    - ``color`` ('primary' or 'secondary' or 'disabled' or 'placeholder' or 'accent' or 'inherit'):
      Text color. Defaults to 'secondary' for the 'supporting' type, 'primary' for all others.
    - ``weight`` ('normal' or 'medium' or 'semibold' or 'bold'): Font weight override.
    - ``display`` ('inline' or 'block'): Display type. Silently overridden to 'block' when maxLines
      > 0 or hasCapsize is true.
    - ``as`` ('span' or 'p' or 'div' or 'label'): HTML element to render.
    - ``maxLines`` (number): Maximum lines before truncation. 0 means no truncation. When set, shows
      a tooltip on hover if content is truncated.
    - ``hasTruncateTooltip`` (boolean or 'above' or 'below' or 'start' or 'end'): Controls tooltip
      behavior for truncated text. true shows the tooltip at the default position, false
      disables it, or a placement string ('above' or 'below' or 'start' or 'end') sets a
      specific position.
    - ``wordBreak`` ('break-word' or 'break-all'): Word break behavior when truncating. Defaults to
      'break-all' for single-line truncation, 'break-word' otherwise.
    - ``textWrap`` ('wrap' or 'nowrap' or 'balance' or 'pretty'): Text wrapping behavior.
    - ``justify`` ('start' or 'center' or 'end'): Text alignment (justification). Uses logical
      values (start/end) for i18n/RTL compatibility.
    - ``hasCapsize`` (boolean): Enable optical alignment using text-box-trim. Forces block display.
    - ``hasStrikethrough`` (boolean): Apply strikethrough text decoration.
    - ``hasTabularNumbers`` (boolean): Use tabular (monospace) numbers for aligned numeric data.
    - ``id`` (string): HTML id attribute.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Text>.
    """

    def __init__(self, text: str, *, props: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__("Text", text=text, props=props, **kwargs)


class Heading(Widget):
    """Render a semantic Astryx heading.

    Parameters
    ----------
    text : str
        Text content synchronized to the frontend component.
    level : int, default 3
        Heading level from 1 through 6.
    props : Mapping[str, Any] | None
        JSON-safe Heading props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Heading props forwarded to Astryx.

    Supported Astryx props include:

    - ``level`` (1 or 2 or 3 or 4 or 5 or 6; required): Heading level. Determines the semantic HTML
      element (h1-h6) and the visual styling from the theme (unless 'type' is set).
    - ``type`` ('display-1' or 'display-2' or 'display-3'): Display type variant. Overrides the
      visual styling from 'level' with display-scale sizing (larger, lighter weight, tighter
      line-height). The 'level' still determines the HTML element for accessibility. Use for
      hero banners, marketing headlines, and data callouts.
    - ``children`` (ReactNode; required): Heading content.
    - ``accessibilityLevel`` (1 or 2 or 3 or 4 or 5 or 6): Accessibility level override. When set
      and different from 'level', applies 'aria-level' so the document outline differs from the
      visual style.
    - ``color`` ('primary' or 'secondary' or 'disabled' or 'placeholder' or 'accent' or 'inherit'):
      Text color.
    - ``display`` ('inline' or 'block'): Display type. Silently overridden to 'block' when maxLines
      > 0 or hasCapsize is true.
    - ``maxLines`` (number): Maximum lines before truncation. 0 means no truncation. When set, shows
      a tooltip on hover if content is truncated.
    - ``hasTruncateTooltip`` (boolean or 'above' or 'below' or 'start' or 'end'): Controls tooltip
      behavior for truncated text. true shows the tooltip at the default position, false
      disables it, or a placement string ('above' or 'below' or 'start' or 'end') sets a
      specific position.
    - ``wordBreak`` ('break-word' or 'break-all'): Word break behavior when truncating. Defaults to
      'break-all' for single-line truncation, 'break-word' otherwise.
    - ``textWrap`` ('wrap' or 'nowrap' or 'balance' or 'pretty'): Text wrapping behavior.
    - ``justify`` ('start' or 'center' or 'end'): Text alignment (justification). Uses logical
      values (start/end) for i18n/RTL compatibility.
    - ``hasCapsize`` (boolean): Enable optical alignment using text-box-trim. Forces block display.
    - ``hasStrikethrough`` (boolean): Apply strikethrough text decoration.
    - ``id`` (string): HTML id attribute.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Heading>.
    """

    def __init__(self, text: str, *, level: int = 3, props: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        if not 1 <= level <= 6:
            raise ValueError("heading level must be between 1 and 6")
        super().__init__("Heading", text=text, props={"level": level, **dict(props or {}), **kwargs})


class Badge(Widget):
    """Render a compact status or category badge.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    variant : str, default 'neutral'
        Astryx visual variant.
    **props : Any
        JSON-safe Badge props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Badge props forwarded to Astryx.

    Supported Astryx props include:

    - ``variant`` ('neutral' or 'info' or 'success' or 'warning' or 'error' or 'blue' or 'cyan' or
      'green' or 'orange' or 'pink' or 'purple' or 'red' or 'teal' or 'yellow'): Visual style
      variant. Semantic variants (neutral, info, success, warning, error) use solid backgrounds.
      Non-semantic color variants use tinted backgrounds with colored text for categorization
      and tagging.
    - ``label`` (ReactNode): Badge text content.
    - ``icon`` (ReactNode): Optional leading icon.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Badge>.
    """

    def __init__(self, label: str, *, variant: str = "neutral", **props: Any) -> None:
        super().__init__("Badge", label=label, variant=variant, props=props)


class Button(Widget):
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
        JSON-safe Button props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Button props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessible label. Rendered as visible text by default; used as
      aria-label when isIconOnly is true.
    - ``variant`` ('primary' or 'secondary' or 'ghost' or 'destructive'): Visual style variant.
    - ``size`` ('sm' or 'md' or 'lg'): Size variant.
    - ``type`` ('button' or 'submit' or 'reset'): HTML button type attribute.
    - ``name`` (string): HTML name attribute for form submission.
    - ``value`` (string or number or readonly string[]): HTML value attribute for form submission.
    - ``form`` (string): Associates the button with a form element by ID.
    - ``isLoading`` (boolean): Shows a loading spinner and disables interaction. Announces "Loading"
      via a live region.
    - ``isInterruptible`` (boolean): Keep the button clickable while a clickAction is pending: the
      spinner and aria-busy still show, but the button is not disabled and the action is not
      deduped, so a re-click lands and interrupts the in-flight action with a fresh one.
    - ``isDisabled`` (boolean): Disables the button. When a tooltip is present, uses aria-disabled
      instead of native disabled so the button stays focusable.
    - ``icon`` (ReactNode): Icon element rendered before the label text.
    - ``isIconOnly`` (boolean): When true, renders as a square icon-only button with label as
      aria-label. Requires icon. Tip: for a dedicated icon-only button component, use IconButton
      from '@astryxdesign/core/IconButton' instead.
    - ``children`` (ReactNode): Optional override for visible text. When provided, displayed instead
      of label, but label is still required (it provides the accessible name). For most cases,
      just use label alone: <Button label="Save" />.
    - ``endContent`` (ReactElement<IconProps> or ReactElement<BadgeProps>): Trailing icon or badge
      rendered after the label. Ignored when isIconOnly is true. Color is inherited from the
      button variant.
    - ``tooltip`` (string): Tooltip text shown on hover.
    - ``onClick`` ((e: MouseEvent) => void): Standard click handler (passed through from
      ButtonHTMLAttributes).
    - ``clickAction`` ((e: MouseEvent) => void or Promise<void>): Async click handler. Shows loading
      state while the returned promise is pending.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Button>.
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


class IconButton(Widget):
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
        JSON-safe IconButton props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe IconButton props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessible label. Used as aria-label (not rendered as visible
      text).
    - ``icon`` (ReactNode; required): Icon element rendered inside the button.
    - ``variant`` ('primary' or 'secondary' or 'ghost' or 'destructive'): Visual style variant.
    - ``size`` ('sm' or 'md' or 'lg'): Size variant.
    - ``isLoading`` (boolean): Shows a loading spinner and disables interaction.
    - ``isDisabled`` (boolean): Disables the button.
    - ``tooltip`` (string): Tooltip text shown on hover.
    - ``onClick`` ((e: MouseEvent) => void): Standard click handler.
    - ``clickAction`` ((e: MouseEvent) => void or Promise<void>): Async click handler with automatic
      loading state.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/IconButton>.
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


class ToggleButton(Widget):
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
        JSON-safe ToggleButton props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe ToggleButton props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessible label for the button. Used as visible text, or as
      aria-label for icon-only buttons.
    - ``isPressed`` (boolean): Whether the button is currently pressed. Ignored when inside a group.
    - ``onPressedChange`` ((isPressed: boolean, event: MouseEvent) => void): Called when pressed
      state should change. Receives the next state and the click event; call
      event.preventDefault() to skip pressedChangeAction. Ignored when inside a group.
    - ``pressedChangeAction`` ((isPressed: boolean) => void or Promise<void>): Action handler for
      API- or navigation-backed toggles, run in a transition. Shows an optimistic pressed state
      immediately and a spinner while pending; the button stays interruptible by re-clicks.
    - ``size`` ('sm' or 'md' or 'lg'): Button size. Defaults to group size when inside a group.
    - ``isDisabled`` (boolean): Whether the button is disabled.
    - ``isLoading`` (boolean): Whether the button shows a loading spinner.
    - ``icon`` (ReactNode): Icon element. When provided without children, button becomes icon-only
      with tooltip from label.
    - ``isIconOnly`` (boolean): When true, renders as a square icon-only button with 'label' as the
      aria-label and an automatic tooltip from the label.
    - ``pressedIcon`` (ReactNode): Icon shown when pressed. Falls back to icon if not provided.
    - ``children`` (ReactNode): Visible content. If omitted with icon, button becomes icon-only.
    - ``tooltip`` (string): Tooltip text shown on hover.
    - ``value`` (string): Value identifier when used inside ToggleButtonGroup. Required in groups.
    - ``data-testid`` (string): Test selector for automated testing frameworks.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/ToggleButton>.
    """

    def __init__(self, value: bool = False, *, label: str, disabled: bool = False, **props: Any) -> None:
        super().__init__("ToggleButton", label=label, value=value, disabled=disabled, props=props)


class TextInput(Widget):
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
        JSON-safe TextInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe TextInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``type`` ('text' or 'password' or 'email'): The HTML input type.
    - ``label`` (string; required): Label text for the input: always rendered for accessibility.
    - ``value`` (string; required): Current value of the input.
    - ``onChange`` ((value: string, e: ChangeEvent<HTMLInputElement>) => void): Callback fired when
      the input value changes.
    - ``changeAction`` ((value: string, e: ChangeEvent<HTMLInputElement>) => void or Promise<void>):
      Async action fired after onChange (if not prevented). Triggers optimistic update and shows
      a loading spinner while pending.
    - ``size`` ('sm' or 'md' or 'lg'): Size variant of the input.
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible to screen
      readers.
    - ``description`` (string): Description text displayed between the label and input.
    - ``isOptional`` (boolean): Displays an "Optional" indicator next to the label. Mutually
      exclusive with isRequired.
    - ``isRequired`` (boolean): Displays a "Required" indicator next to the label and sets
      aria-required. Mutually exclusive with isOptional.
    - ``isDisabled`` (boolean): Disables the input, preventing interaction and dimming the element.
    - ``isLoading`` (boolean): Puts the input in a loading state, showing a spinner and setting
      aria-busy.
    - ``placeholder`` (string): Placeholder text shown when the input is empty.
    - ``labelTooltip`` (string): Tooltip text displayed in an info icon at the end of the label.
    - ``startIcon`` (IconType): SVG icon component displayed at the start of the input. See 'npx
      astryx docs icons' for valid semantic names.
    - ``status`` ({type: 'error' or 'warning' or 'success', message?: string}): Validation status:
      applies a colored border and status icon. If message is provided, displays a floating
      message below the input. Error type also sets aria-invalid.
    - ``hasClear`` (boolean): Shows a clear (x) button when the input has a value. Clicking it
      clears the value and returns focus to the input.
    - ``hasAutoFocus`` (boolean): Automatically focuses the input on mount.
    - ``htmlName`` (string): The HTML name attribute for the input, useful for form submissions.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/TextInput>.
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


class TextArea(Widget):
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
        JSON-safe TextArea props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe TextArea props forwarded to Astryx.

    Supported Astryx props include:

    - ``ref`` (React.Ref<HTMLTextAreaElement>): Ref forwarded to the underlying <textarea> element.
    - ``label`` (string; required): Label text for the textarea. Always rendered for accessibility.
    - ``value`` (string; required): Current value of the textarea.
    - ``onChange`` ((value: string, e: ChangeEvent<HTMLTextAreaElement>) => void): Callback fired
      when the textarea value changes.
    - ``changeAction`` ((value: string, e: ChangeEvent<HTMLTextAreaElement>) => void or
      Promise<void>): Async action fired after onChange inside a React transition. Enables
      optimistic updates via useOptimistic.
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible to screen
      readers.
    - ``description`` (string): Helper text displayed between the label and textarea.
    - ``isOptional`` (boolean): Displays an "Optional" indicator next to the label. Mutually
      exclusive with isRequired.
    - ``isRequired`` (boolean): Displays a "Required" indicator next to the label and sets
      aria-required. Mutually exclusive with isOptional.
    - ``isDisabled`` (boolean): Disables the textarea, preventing interaction.
    - ``isLoading`` (boolean): Puts the textarea in a loading state, showing a spinner inside the
      input.
    - ``placeholder`` (string): Placeholder text shown when the textarea is empty.
    - ``rows`` (number): Number of visible text rows.
    - ``maxLength`` (number): Maximum number of characters allowed. When set, a character counter
      (current/max) is displayed below the textarea. Does not enforce the limit natively; the
      counter shows error styling when exceeded.
    - ``status`` ({ type: 'warning' or 'error' or 'success'; message?: string }): Status indicator
      that applies a colored border and icon. An optional message is displayed in a floating box
      below the textarea.
    - ``labelTooltip`` (string): Tooltip text displayed in an info icon at the end of the label.
    - ``startIcon`` (IconType): Icon component rendered inside the leading edge of the textarea
      wrapper. See 'npx astryx docs icons' for valid semantic names.
    - ``hasSpellCheck`` (boolean): Enables or disables browser spell checking.
    - ``hasAutoFocus`` (boolean): Automatically focuses the textarea on mount.
    - ``size`` ('sm' or 'md' or 'lg'): Size of the textarea, affecting internal padding. Height is
      controlled by rows, not size.
    - ``onPaste`` ((e: ClipboardEvent<HTMLTextAreaElement>) => void): Callback fired when content is
      pasted into the textarea.
    - ``htmlName`` (string): HTML name attribute for the textarea element, useful for form
      submissions.
    - ``onFocus`` ((e: FocusEvent<HTMLTextAreaElement>) => void): Callback fired when the textarea
      receives focus.
    - ``onBlur`` ((e: FocusEvent<HTMLTextAreaElement>) => void): Callback fired when the textarea
      loses focus.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/TextArea>.
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


class NumberInput(Widget):
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
        JSON-safe NumberInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe NumberInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for the input (always rendered for accessibility).
    - ``value`` (number or null or undefined; required): Current value of the input.
    - ``onChange`` ((value: number) => void; required): Callback fired when input value changes
      (only on valid input).
    - ``size`` ('sm' or 'md' or 'lg'): Size variant.
    - ``isLabelHidden`` (boolean): Visually hide the label (still accessible to screen readers).
    - ``description`` (string): Description text displayed between the label and input.
    - ``isOptional`` (boolean): Whether the field is optional (mutually exclusive with isRequired).
    - ``isRequired`` (boolean): Whether the field is required (mutually exclusive with isOptional).
    - ``isDisabled`` (boolean): Whether the input is disabled.
    - ``placeholder`` (string): Placeholder text.
    - ``labelTooltip`` (string): Tooltip text to display in an info icon at the end of the label.
    - ``startIcon`` (IconType): Icon to display at the start of the input. See 'npx astryx docs
      icons' for valid semantic names.
    - ``labelIcon`` (IconType): Icon to display before the label text. See 'npx astryx docs icons'
      for valid semantic names.
    - ``status`` ({type: 'error' or 'warning' or 'success', message?: string}): Validation status
      with optional message.
    - ``min`` (number or null): Minimum value allowed.
    - ``max`` (number or null): Maximum value allowed.
    - ``step`` (number or null): Step increment for the input.
    - ``units`` (string or null): Units text to display at the end of the input (e.g., "%" or "GB").
    - ``isIntegerOnly`` (boolean): Only allow integer values (no floating point).
    - ``hasClear`` (boolean): Shows a clear (x) button when the input has a value. When true, the
      onChange callback also accepts null to signal the user cleared the input.
    - ``htmlName`` (string): HTML name attribute for form submissions.
    - ``autoComplete`` (string): HTML autocomplete attribute.
    - ``hasAutoFocus`` (boolean): Whether to focus the input on mount.
    - ``onFocus`` ((e: FocusEvent<HTMLInputElement>) => void): Callback fired when the input
      receives focus.
    - ``onBlur`` ((e: FocusEvent<HTMLInputElement>) => void): Callback fired when the input loses
      focus.
    - ``onEnter`` (() => void): Callback fired when the user presses the Enter key.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/NumberInput>.
    """

    def __init__(self, value: int | float | None = None, *, label: str = "", disabled: bool = False, **props: Any) -> None:
        super().__init__("NumberInput", label=label, value=value, disabled=disabled, props=props)


class Slider(Widget):
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
        JSON-safe Slider props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Slider props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text (always rendered for accessibility).
    - ``value`` (number or [number, number]; required): Current value: a 'number' for single thumb
      mode or '[number, number]' for range mode.
    - ``onChange`` ((value: number) => void or (value: [number, number]) => void): Callback fired on
      value change during drag.
    - ``onChangeEnd`` ((value: number) => void or (value: [number, number]) => void): Callback fired
      when drag ends.
    - ``min`` (number): Minimum value.
    - ``max`` (number): Maximum value.
    - ``step`` (number): Step increment.
    - ``orientation`` ('horizontal' or 'vertical'): Orientation of the slider.
    - ``formatValue`` ((value: number) => string): Custom value formatting function used for display
      and 'aria-valuetext'.
    - ``valueDisplay`` ('tooltip' or 'text' or 'none'): How the current value is displayed.
    - ``marks`` (Array<{ value: number; label?: string }>): Tick marks at specified positions with
      optional labels.
    - ``minStepsBetweenThumbs`` (number): Minimum number of steps between thumbs in range mode;
      prevents thumbs from overlapping.
    - ``isDisabled`` (boolean): Whether the slider is disabled.
    - ``isOptional`` (boolean): Whether the field is optional.
    - ``isRequired`` (boolean): Whether the field is required.
    - ``isLabelHidden`` (boolean): Whether to visually hide the label.
    - ``description`` (string): Description text rendered below the label.
    - ``status`` (InputStatus): Status indicator object ('{ type, message }') for validation
      feedback.
    - ``labelTooltip`` (string): Tooltip text for an info icon displayed next to the label.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Slider>.
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


class Checkbox(Widget):
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
        JSON-safe CheckboxInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe CheckboxInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``ref`` (React.Ref<HTMLInputElement>): Ref forwarded to the underlying <input> element.
    - ``label`` (string; required): Label text for the checkbox (always rendered for accessibility).
    - ``isLabelHidden`` (boolean): Whether to visually hide the label (still accessible to screen
      readers).
    - ``description`` (string): Description text displayed below the label.
    - ``value`` (boolean or 'indeterminate'; required): Whether the checkbox is checked, unchecked,
      or indeterminate.
    - ``onChange`` ((checked: boolean, e: ChangeEvent<HTMLInputElement>) => void): Callback fired
      when the checkbox state changes.
    - ``changeAction`` ((checked: boolean, e: ChangeEvent<HTMLInputElement>) => void or
      Promise<void>): Async action on change. Fires after onChange if not prevented. Shows
      loading spinner while pending.
    - ``isLoading`` (boolean): Whether the checkbox is in a loading state. Shows spinner and
      prevents interaction.
    - ``isDisabled`` (boolean): Whether the checkbox is disabled.
    - ``isReadOnly`` (boolean): Whether the checkbox is read-only. Displays the current state at
      full opacity but prevents interaction. Unlike 'isDisabled', read-only checkboxes are not
      visually dimmed.
    - ``isOptional`` (boolean): Whether the field is optional. Mutually exclusive with isRequired.
    - ``isRequired`` (boolean): Whether the checkbox is required. Mutually exclusive with
      isOptional.
    - ``size`` ('sm' or 'md'): The size of the checkbox. sm for compact layouts, md for default.
    - ``onFocus`` ((e: FocusEvent<HTMLInputElement>) => void): Callback fired when the checkbox
      receives focus.
    - ``onBlur`` ((e: FocusEvent<HTMLInputElement>) => void): Callback fired when the checkbox loses
      focus.
    - ``labelIcon`` (IconType): Icon to display before the label text. See 'npx astryx docs icons'
      for valid semantic names.
    - ``status`` ({ type: 'error' or 'warning' or 'success', message: string }): Status indicator.
      Displays a colored message box below the checkbox and sets aria-invalid for errors.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/CheckboxInput>.
    """

    def __init__(self, value: bool = False, *, label: str = "", disabled: bool = False, **props: Any) -> None:
        super().__init__("CheckboxInput", label=label, value=value, disabled=disabled, props=props)


class Switch(Widget):
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
        JSON-safe Switch props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Switch props forwarded to Astryx.

    Supported Astryx props include:

    - ``ref`` (React.Ref<HTMLInputElement>): Ref forwarded to the underlying <input> element.
    - ``label`` (string; required): Label text for the switch (always rendered for accessibility).
    - ``value`` (boolean; required): Whether the switch is on or off.
    - ``onChange`` ((checked: boolean, e: ChangeEvent<HTMLInputElement>) => void): Callback fired
      when the switch state changes.
    - ``changeAction`` ((checked: boolean, e: ChangeEvent<HTMLInputElement>) => void or
      Promise<void>): Async action fired after onChange. Triggers optimistic UI and shows a
      loading spinner until the promise resolves.
    - ``isLoading`` (boolean): Whether the switch is in a loading state, showing a spinner inside
      the thumb.
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible to screen
      readers.
    - ``description`` (string): Description text displayed below the label.
    - ``isDisabled`` (boolean): Whether the switch is disabled.
    - ``isOptional`` (boolean): Whether the field is optional. Mutually exclusive with isRequired.
    - ``isRequired`` (boolean): Whether the switch is required. Mutually exclusive with isOptional.
    - ``status`` (InputStatus): Status indicator with type and message. Displays a colored message
      box below the switch and sets aria-invalid when type is "error".
    - ``onFocus`` ((e: FocusEvent<HTMLInputElement>) => void): Callback fired when the switch
      receives focus.
    - ``onBlur`` ((e: FocusEvent<HTMLInputElement>) => void): Callback fired when the switch loses
      focus.
    - ``labelIcon`` (IconType): Icon displayed before the label text. See 'npx astryx docs icons'
      for valid semantic names.
    - ``labelTooltip`` (string): Tooltip text shown in an info icon at the end of the label.
    - ``labelPosition`` ('start' or 'end'): Which side of the switch the label appears on. "start"
      places the label before the switch.
    - ``labelSpacing`` ('default' or 'spread'): Spacing behavior between label and switch. "spread"
      pushes them to opposite ends of the container (full width).

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Switch>.
    """

    def __init__(self, value: bool = False, *, label: str = "", disabled: bool = False, **props: Any) -> None:
        super().__init__("Switch", label=label, value=value, disabled=disabled, props=props)


class Selector(Widget):
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
        JSON-safe Selector props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Selector props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for accessibility.
    - ``options`` (SelectorOption[]; required): Array of items: strings, objects with
      value/label/icon/disabled, dividers ({type: "divider"}), or sections ({type: "section",
      title, items}).
    - ``value`` (string): Currently selected value.
    - ``onChange`` ((value: string) => void): Callback fired when the selection changes.
    - ``hasClear`` (boolean): Shows a clear (x) button when a value is selected. When true, onChange
      also accepts null to signal the user cleared the selection.
    - ``hasSearch`` (boolean): Whether to show a search input for filtering options.
    - ``searchPlaceholder`` (string): Placeholder text for the search input.
    - ``placeholder`` (string): Placeholder text shown when no value is selected.
    - ``size`` ('sm' or 'md' or 'lg'): Size variant for the selector.
    - ``isDisabled`` (boolean): Disables the selector.
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible.
    - ``description`` (string): Helper text displayed below the label.
    - ``isOptional`` (boolean): Marks the field as optional.
    - ``isRequired`` (boolean): Marks the field as required.
    - ``status`` ({type: 'error' or 'warning' or 'success', message?: string}): Validation status
      with an optional message.
    - ``renderOption`` ((option: SelectorOptionData) => ReactNode): Custom render function for each
      selectable option in the dropdown. Use this instead of JSX children; dividers and sections
      are rendered by the selector.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Selector>.
    """

    def __init__(self, options: Iterable[Any] | Mapping[str, Any], value: str | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("Selector", label=label, value=value, props={"options": _option_records(options), **props})


class MultiSelector(Widget):
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
        JSON-safe MultiSelector props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe MultiSelector props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for the multi-selector, always rendered for
      accessibility unless hidden visually.
    - ``isLabelHidden`` (boolean; default false): Visually hides the label while keeping it
      available to screen readers.
    - ``description`` (string): Helper text displayed between the label and selector.
    - ``isOptional`` (boolean; default false): Marks the field as optional; mutually exclusive with
      isRequired.
    - ``isRequired`` (boolean; default false): Marks the field as required; mutually exclusive with
      isOptional.
    - ``isDisabled`` (boolean; default false): Disables the selector.
    - ``options`` (option[]; required): Options displayed in the selector. Astryx accepts strings,
      option objects, dividers, and sections.
    - ``value`` (string[]; required): Selected option values.
    - ``onChange`` ((value: string[]) => void; required): Called when selected values change.
    - ``changeAction`` ((value: string[]) => void or Promise<void>): Async action fired after
      onChange.
    - ``isLoading`` (boolean; default false): Shows the selector loading state.
    - ``placeholder`` (string; default 'Select...'): Placeholder text when no value is selected.
    - ``size`` ('sm' or 'md' or 'lg'; default 'md'): Selector size.
    - ``status`` (MultiSelectorStatus): Validation status for warning, error, or success states.
    - ``width`` (number or string): Field width. Numbers are pixels; strings are used as CSS values.
    - ``labelTooltip`` (string): Tooltip text for an info icon at the end of the label.
    - ``startIcon`` (ReactNode or IconType): Icon displayed at the start of the trigger.
    - ``hasClear`` (boolean; default false): Shows a clear button when values are selected.
    - ``hasSelectAll`` (boolean; default false): Shows a select-all checkbox.
    - ``selectAllLabel`` (string; default 'Select all'): Label for the select-all checkbox.
    - ``hasSearch`` (boolean; default false): Shows a search input in the dropdown.
    - ``searchPlaceholder`` (string; default 'Search...'): Placeholder text for the search input.
    - ``triggerDisplay`` ('count' or 'labels' or 'badges'; default 'count'): Controls how selected
      items are summarized in the trigger.
    - ``maxBadges`` (number; default 3): Maximum visible badges before showing a +N summary.
    - ``renderOption`` ((option: MultiSelectorOptionData) => ReactNode): Custom render function for
      selectable options.
    - ``isDefaultOpen`` (boolean; default false): Opens the dropdown on mount, useful for previews.
    - ``data-testid`` (string): Test selector for automated testing.
    - ``xstyle`` (StyleXStyles): StyleX layout customization.
    - ``className`` (string): CSS class names for the root element.
    - ``style`` (CSSProperties): Inline styles for the root element.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/MultiSelector>.
    """

    def __init__(self, options: Iterable[Any] | Mapping[str, Any], value: Iterable[str] = (), *, label: str = "", **props: Any) -> None:
        super().__init__("MultiSelector", label=label, value=list(value), props={"options": _option_records(options), **props})


class DateInput(Widget):
    """Render an Astryx date input.

    Parameters
    ----------
    value : str | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    **props : Any
        JSON-safe DateInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe DateInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text.
    - ``isLabelHidden`` (boolean): Visually hide the label.
    - ``description`` (string): Helper text displayed below the label.
    - ``isOptional`` (boolean): Show an "(optional)" indicator next to the label.
    - ``isRequired`` (boolean): Mark the field as required.
    - ``isDisabled`` (boolean): Disable the input and calendar.
    - ``value`` (ISODateString): Selected date in YYYY-MM-DD format.
    - ``onChange`` ((value: ISODateString or undefined) => void): Callback invoked when the selected
      date changes.
    - ``changeAction`` ((value: ISODateString or undefined) => void or Promise<void>): Async action
      fired after onChange. Drives optimistic UI updates via useTransition.
    - ``isLoading`` (boolean): Whether the input is in a loading state. Disables interaction and
      shows a spinner.
    - ``min`` (ISODateString): Minimum selectable date (YYYY-MM-DD).
    - ``max`` (ISODateString): Maximum selectable date (YYYY-MM-DD).
    - ``dateConstraints`` (Array<(date: Date) => boolean>): Array of custom constraint functions
      that disable specific dates.
    - ``placeholder`` (string): Placeholder text shown in the text input.
    - ``size`` ('sm' or 'md' or 'lg'): Size of the input control.
    - ``status`` (InputStatus): Status indicator object for error, warning, or success states with a
      message.
    - ``labelTooltip`` (string): Tooltip text displayed via an info icon at the end of the label.
    - ``hasClear`` (boolean): Shows a clear (x) button when a date value is set. Clicking it clears
      the value and returns focus to the input.
    - ``numberOfMonths`` (1 or 2): Number of months displayed simultaneously in the calendar
      popover.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/DateInput>.
    """

    def __init__(self, value: str | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("DateInput", label=label, value=value, props=props)


class TimeInput(Widget):
    """Render an Astryx time input.

    Parameters
    ----------
    value : str | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    **props : Any
        JSON-safe TimeInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe TimeInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for the input (required for accessibility).
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible to screen
      readers.
    - ``description`` (string): Description text displayed between the label and input.
    - ``isOptional`` (boolean): Shows an "(optional)" indicator next to the label. Mutually
      exclusive with isRequired.
    - ``isRequired`` (boolean): Marks the field as required and sets aria-required. Mutually
      exclusive with isOptional.
    - ``isDisabled`` (boolean): Disables the input and suppresses interactions.
    - ``value`` (ISOTimeString): Controlled time value in ISO format (HH:MM or HH:MM:SS).
    - ``onChange`` ((value: ISOTimeString or undefined) => void): Callback fired when the time
      changes. Receives undefined when the input is cleared.
    - ``changeAction`` ((value: ISOTimeString or undefined) => void or Promise<void>): Async action
      fired after onChange. Wrapped in a React transition to provide optimistic UI; triggers the
      loading spinner while pending.
    - ``isLoading`` (boolean): Puts the input into a loading state, displaying a spinner.
    - ``min`` (ISOTimeString): Minimum selectable time in ISO format. Values outside the range are
      rejected.
    - ``max`` (ISOTimeString): Maximum selectable time in ISO format. Values outside the range are
      rejected.
    - ``hasSeconds`` (boolean): Includes seconds in the time display and parsing.
    - ``hasClear`` (boolean): Shows a clear button when a value is set and the input is not
      disabled.
    - ``hourFormat`` ('12h' or '24h'): Controls the display format. '12h' shows AM/PM (e.g. '2:30
      PM'); '24h' uses 24-hour notation (e.g. '14:30').
    - ``increment`` (number): Number of minutes to add or subtract when the user presses the up or
      down arrow key.
    - ``placeholder`` (string): Placeholder text shown when no time is selected. When the input is
      focused and empty, a format hint overrides this text.
    - ``size`` ('sm' or 'md' or 'lg'): Controls the height of the input element.
    - ``status`` (InputStatus): Status indicator that colors the border and displays an icon. When a
      message is provided it is rendered below the input.
    - ``labelTooltip`` (string): Tooltip text rendered as an info icon at the end of the label row.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/TimeInput>.
    """

    def __init__(self, value: str | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("TimeInput", label=label, value=value, props=props)


class DateTimeInput(Widget):
    """Render an Astryx date-time input.

    Parameters
    ----------
    value : str | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    **props : Any
        JSON-safe DateTimeInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe DateTimeInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text.
    - ``isLabelHidden`` (boolean): Visually hide the label.
    - ``description`` (string): Helper text displayed below the label.
    - ``isOptional`` (boolean): Show an "(optional)" indicator next to the label.
    - ``isRequired`` (boolean): Mark the field as required.
    - ``isDisabled`` (boolean): Disable the input and picker.
    - ``value`` (ISODateTimeString): Selected datetime in ISO 8601 format (YYYY-MM-DDTHH:MM or
      YYYY-MM-DDTHH:MM:SS).
    - ``onChange`` ((value: ISODateTimeString or undefined) => void; required): Callback invoked
      when the selected datetime changes.
    - ``changeAction`` ((value: ISODateTimeString or undefined) => void or Promise<void>): Async
      action fired after onChange. Drives optimistic UI updates via useTransition.
    - ``isLoading`` (boolean): Whether the input is in a loading state. Disables interaction and
      shows a spinner.
    - ``min`` (ISODateTimeString): Minimum selectable datetime. Constrains both date and time
      selection.
    - ``max`` (ISODateTimeString): Maximum selectable datetime. Constrains both date and time
      selection.
    - ``dateConstraints`` (Array<(date: Date) => boolean>): Array of custom constraint functions
      that disable specific dates.
    - ``hasSeconds`` (boolean): Include seconds in the time portion.
    - ``hourFormat`` ('12h' or '24h'): Hour display format. '12h' shows AM/PM; '24h' uses 24-hour
      notation.
    - ``timeIncrement`` (number): Minutes to add or subtract when using arrow keys in the time
      input.
    - ``hasClear`` (boolean): Shows a clear button when a datetime value is set.
    - ``placeholder`` (string): Placeholder text shown in the date portion when no date is selected.
    - ``timePlaceholder`` (string): Placeholder text shown in the time portion when no time is
      selected.
    - ``timeLabel`` (string): Accessible label for the time portion. Defaults to "{label} time" so
      it is tied to the field label and localizable.
    - ``size`` ('sm' or 'md' or 'lg'): Size of the input control.
    - ``status`` (InputStatus): Status indicator object for error, warning, or success states with a
      message.
    - ``labelTooltip`` (string): Tooltip text displayed via an info icon at the end of the label.
    - ``numberOfMonths`` (1 or 2): Number of months displayed simultaneously in the calendar.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/DateTimeInput>.
    """

    def __init__(self, value: str | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("DateTimeInput", label=label, value=value, props=props)


class DateRangeInput(Widget):
    """Render an Astryx date-range input.

    Parameters
    ----------
    value : Mapping[str, str] | None
        Synchronized component value.
    label : str, default ''
        Visible or accessible label for the component.
    **props : Any
        JSON-safe DateRangeInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe DateRangeInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text.
    - ``isLabelHidden`` (boolean): Visually hide the label.
    - ``description`` (string): Helper text displayed below the label.
    - ``isOptional`` (boolean): Show an "(optional)" indicator.
    - ``isRequired`` (boolean): Mark the field as required.
    - ``isDisabled`` (boolean): Disable the trigger and picker.
    - ``value`` (DateRange or null; required): Selected date range ({start, end} in ISO format), or
      null.
    - ``onChange`` ((value: DateRange or null) => void; required): Callback when the range changes.
      Called with null on clear.
    - ``changeAction`` ((value: DateRange or null) => void or Promise<void>): Async action fired
      after onChange. Drives optimistic UI updates via useTransition.
    - ``isLoading`` (boolean): Whether the input is in a loading state. Disables interaction and
      shows a spinner.
    - ``min`` (ISODateString): Minimum selectable date.
    - ``max`` (ISODateString): Maximum selectable date.
    - ``dateConstraints`` (Array<(date: Date) => boolean>): Custom constraint functions to disable
      specific dates.
    - ``presets`` (Array<DateRangePreset>): Preset ranges shown as quick-select options beside the
      calendar.
    - ``hasClear`` (boolean): Shows a clear button when a range is selected.
    - ``placeholder`` (string): Placeholder text when no range is selected.
    - ``size`` ('sm' or 'md' or 'lg'): Size of the trigger.
    - ``status`` (InputStatus): Status indicator for error, warning, or success states.
    - ``labelTooltip`` (string): Tooltip text via info icon at label end.
    - ``numberOfMonths`` (1 or 2): Number of months in the calendar.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/DateRangeInput>.
    """

    def __init__(self, value: Mapping[str, str] | None = None, *, label: str = "", **props: Any) -> None:
        super().__init__("DateRangeInput", label=label, value=value, props=props)


class Stack(Widget):
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
    """

    def __init__(self, children: ChildInput = None, *, direction: str = "vertical", gap: int | float = 2, **props: Any) -> None:
        super().__init__("Stack", children, props={"direction": direction, "gap": gap, **props})


class Grid(Widget):
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
        JSON-safe Grid props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Grid props forwarded to Astryx.

    Supported Astryx props include:

    - ``columns`` (number or {minWidth: number, max?: number, repeat?: 'fill' or 'fit'}): Column
      configuration. Use a number for fixed columns (e.g. 'columns={3}'). Use an object for
      responsive columns: 'minWidth' sets the minimum column width in px, 'repeat' controls
      track behavior ('"fill"' preserves empty tracks for consistent widths, '"fit"' collapses
      empty tracks so items stretch; defaults to '"fill"'), and 'max' caps the maximum number of
      columns.
    - ``minChildWidth`` (number): Deprecated: use 'columns={{minWidth: 280}}' instead. Minimum item
      width in px; enables responsive auto-fit.
    - ``width`` (number or string): Container width.
    - ``height`` (number or string): Container height.
    - ``gap`` (SpacingStep): Spacing between all items.
    - ``rowGap`` (SpacingStep): Row spacing; overrides 'gap' for the row axis.
    - ``columnGap`` (SpacingStep): Column spacing; overrides 'gap' for the column axis.
    - ``align`` (GridAlignment): Vertical alignment of items.
    - ``justify`` (GridAlignment): Horizontal alignment of items.
    - ``children`` (ReactNode): Grid content.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Grid>.
    """

    def __init__(self, children: ChildInput = None, *, columns: int | Mapping[str, Any] = 2, gap: int | float = 3, **props: Any) -> None:
        super().__init__("Grid", children, props={"columns": _clean_value(columns), "gap": gap, **props})


class Center(Widget):
    """Center child content in an Astryx container.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    axis : str, default 'both'
        Axis used for centering child content.
    **props : Any
        JSON-safe Center props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Center props forwarded to Astryx.

    Supported Astryx props include:

    - ``axis`` ('both' or 'horizontal' or 'vertical'): Which direction(s) to center.
    - ``width`` (number or string): Container width (px or CSS value).
    - ``height`` (number or string): Container height (px or CSS value).
    - ``isInline`` (boolean): Use inline-flex (useful for text/icons).
    - ``children`` (ReactNode): Content to center.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Center>.
    """

    def __init__(self, children: ChildInput = None, *, axis: str = "both", **props: Any) -> None:
        super().__init__("Center", children, props={"axis": axis, **props})


class AspectRatio(Widget):
    """Constrain child content to a fixed aspect ratio.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    ratio : int | float, default '16 / 9'
        Aspect ratio as a numeric width divided by height value.
    **props : Any
        JSON-safe AspectRatio props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe AspectRatio props forwarded to Astryx.

    Supported Astryx props include:

    - ``ratio`` (number; required): Aspect ratio as width/height (e.g. 16/9, 1).
    - ``children`` (ReactNode; required): Content positioned absolutely to fill the container.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/AspectRatio>.
    """

    def __init__(self, children: ChildInput = None, *, ratio: int | float = 16 / 9, **props: Any) -> None:
        super().__init__("AspectRatio", children, props={"ratio": ratio, **props})


class Card(Widget):
    """Render an Astryx card container.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    variant : str, default 'default'
        Astryx visual variant.
    **props : Any
        JSON-safe Card props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Card props forwarded to Astryx.

    Supported Astryx props include:

    - ``width`` (SizeValue): Width of the card (number = pixels, string = used as-is).
    - ``height`` (SizeValue): Height of the card (number = pixels, string = used as-is).
    - ``maxWidth`` (SizeValue): Maximum width of the card.
    - ``minHeight`` (SizeValue): Minimum height of the card.
    - ``children`` (ReactNode): Content to render inside the card.
    - ``padding`` (0 or 0.5 or 1 or 1.5 or 2 or 3 or 4 or 5 or 6 or 8 or 10): Internal padding using
      the spacing scale.
    - ``variant`` ('default' or 'muted' or 'blue' or 'cyan' or 'gray' or 'green' or 'orange' or
      'pink' or 'purple' or 'red' or 'teal' or 'yellow'): Background color variant. 'default'
      uses the standard card background. 'muted' uses the muted background for de-emphasised
      cards. The non-semantic variants use the corresponding '--color-<name>-background' token.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Card>.
    """

    def __init__(self, children: ChildInput = None, *, variant: str = "default", **props: Any) -> None:
        super().__init__("Card", children, variant=variant, props={"variant": variant, **props})


class ClickableCard(Widget):
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
        JSON-safe ClickableCard props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe ClickableCard props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessibility label.
    - ``onClick`` ((event: MouseEvent) => void): Click handler: fires on card surface only.
    - ``href`` (string): Navigation URL.
    - ``target`` (string): Link target.
    - ``isDisabled`` (boolean): Disables the card.
    - ``children`` (ReactNode): Card content.
    - ``padding`` (SpacingStep): Inner padding.
    - ``variant`` ('default' or 'transparent' or 'muted' or 'blue' or 'cyan' or 'gray' or 'green' or
      'orange' or 'pink' or 'purple' or 'red' or 'teal' or 'yellow'): Background color variant.
    - ``width`` (SizeValue): Card width.
    - ``height`` (SizeValue): Card height.
    - ``maxWidth`` (SizeValue): Maximum card width.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/ClickableCard>.
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


class SelectableCard(Widget):
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
        JSON-safe SelectableCard props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe SelectableCard props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessibility label.
    - ``isSelected`` (boolean; required): Controlled selection state.
    - ``onChange`` ((isSelected: boolean) => void; required): Called when toggled.
    - ``isDisabled`` (boolean): Disables the card.
    - ``children`` (ReactNode): Card content.
    - ``padding`` (SpacingStep): Inner padding.
    - ``variant`` ('default' or 'transparent' or 'muted' or 'blue' or 'cyan' or 'gray' or 'green' or
      'orange' or 'pink' or 'purple' or 'red' or 'teal' or 'yellow'): Background color variant.
    - ``width`` (SizeValue): Card width.
    - ``height`` (SizeValue): Card height.
    - ``maxWidth`` (SizeValue): Maximum card width.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/SelectableCard>.
    """

    def __init__(self, children: ChildInput = None, value: bool = False, *, label: str, variant: str = "default", **props: Any) -> None:
        super().__init__("SelectableCard", children, label=label, value=value, variant=variant, props={"variant": variant, **props})


class Section(Widget):
    """Render an Astryx section container.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    variant : str, default 'section'
        Astryx visual variant.
    **props : Any
        JSON-safe Section props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Section props forwarded to Astryx.

    Supported Astryx props include:

    - ``variant`` ('section' or 'transparent' or 'muted'): Background variant applied to the section
      container.
    - ``width`` (SizeValue): Width of the section; a number is interpreted as pixels, a string is
      used as-is.
    - ``height`` (SizeValue): Height of the section; a number is interpreted as pixels, a string is
      used as-is.
    - ``maxWidth`` (SizeValue): Maximum width of the section.
    - ``minHeight`` (SizeValue): Minimum height of the section.
    - ``children`` (ReactNode): Content rendered inside the section.
    - ``dividers`` (Array<'top' or 'bottom' or 'start' or 'end'>): Which sides of the section have
      divider borders.
    - ``padding`` (SpacingStep): Internal padding using the spacing scale (0, 0.5, 1, 1.5, 2, 3, 4,
      5, 6, 8, 10). Use padding={0} for edge-to-edge content.
    - ``paddingBlock`` (SpacingStep): Block (vertical) padding override. Overrides only the
      block-axis padding while preserving inline padding from 'padding' or the container theme
      default. Accepts the spacing scale (0, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10).
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Section>.
    """

    def __init__(self, children: ChildInput = None, *, variant: str = "section", **props: Any) -> None:
        super().__init__("Section", children, variant=variant, props={"variant": variant, **props})


class Divider(Widget):
    """Render an Astryx divider.

    Parameters
    ----------
    orientation : str, default 'horizontal'
        Astryx component option.
    variant : str, default 'subtle'
        Astryx visual variant.
    **props : Any
        JSON-safe Divider props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Divider props forwarded to Astryx.

    Supported Astryx props include:

    - ``orientation`` ('horizontal' or 'vertical'): Orientation of the divider.
    - ``label`` (ReactNode): Optional label centered on the divider.
    - ``variant`` ('subtle' or 'strong'): Visual weight of the divider line.
    - ``isFullBleed`` (boolean): Extend the divider to container edges with negative margins.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Divider>.
    """

    def __init__(self, *, orientation: str = "horizontal", variant: str = "subtle", **props: Any) -> None:
        super().__init__("Divider", variant=variant, props={"orientation": orientation, "variant": variant, **props})


class List(Widget):
    """Render an Astryx list from item records.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    header : str, default ''
        Optional header text or content.
    **props : Any
        JSON-safe List props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe List props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode): List items (ListItem components).
    - ``density`` ('compact' or 'balanced' or 'spacious'): Spacing density for items.
    - ``hasDividers`` (boolean): Show dividers between items.
    - ``header`` (ReactNode): Header content, associated with the list via aria-labelledby.
    - ``listStyle`` ('none' or 'disc' or 'decimal' or 'circle'): List marker style. 'decimal'
      renders an <ol> element instead of <ul>.
    - ``start`` (number): Starting number for ordered lists (listStyle='decimal'). Sets the CSS
      counter to begin at this value.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/List>.
    """

    def __init__(self, items: Iterable[Any], *, header: str = "", **props: Any) -> None:
        super().__init__("List", props={"items": _option_records(items), "header": header or None, **props})


class MetadataList(Widget):
    """Render label-value metadata rows.

    Parameters
    ----------
    items : Iterable[Mapping[str, Any]]
        Item records used by generated child components or static search sources.
    **props : Any
        JSON-safe MetadataList props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe MetadataList props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Metadata items (MetadataListItem components).
    - ``columns`` ('multi' or 'single' or number): Column layout mode.
    - ``label`` ({ position?: 'start' or 'top', width?: number or string }): Label display
      configuration. position controls label placement, width sets a custom label column width.
      Defaults to { position: 'top' } for multi-column layouts.
    - ``maxNumOfItems`` (number): Maximum items to show before collapsing with a show more/less
      toggle.
    - ``orientation`` ('vertical' or 'horizontal'): Layout orientation. Horizontal mode flows items
      in a row with flex-wrap.
    - ``title`` (ReactNode): Optional title or heading above the list.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization. Must be a stylex.create()
      value.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/MetadataList>.
    """

    def __init__(self, items: Iterable[Mapping[str, Any]], **props: Any) -> None:
        super().__init__("MetadataList", props={"items": _clean_value(list(items)), **props})


class Breadcrumbs(Widget):
    """Render Astryx breadcrumbs from item records.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    **props : Any
        JSON-safe Breadcrumbs props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Breadcrumbs props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): BreadcrumbItem elements to render inside the breadcrumb
      trail.
    - ``separator`` (ReactNode): Separator rendered between breadcrumb items.
    - ``variant`` ('default' or 'supporting'): Visual variant: supporting is smaller with secondary
      text styling.
    - ``label`` (string): Accessible label for the nav landmark (aria-label).
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Breadcrumbs>.
    """

    def __init__(self, items: Iterable[Any], **props: Any) -> None:
        super().__init__("Breadcrumbs", props={"items": _option_records(items), **props})


class TabList(Widget):
    """Render an Astryx tab list.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    value : str
        Synchronized component value.
    **props : Any
        JSON-safe TabList props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe TabList props forwarded to Astryx.

    Supported Astryx props include:

    - ``value`` (string; required): The currently selected tab value.
    - ``onChange`` ((value: string) => void; required): Callback fired when a tab is selected.
    - ``size`` ('sm' or 'md' or 'lg'): Size variant applied to all child tabs.
    - ``layout`` ('hug' or 'fill'): Layout mode for tab sizing. 'hug': each tab hugs its content
      width. 'fill': tabs stretch equally to fill the container width.
    - ``hasDivider`` (boolean): Whether to show a bottom border divider under the tab list.
    - ``orientation`` ('horizontal' or 'vertical'): Orientation of the tab strip, controlling which
      arrow keys move focus between tabs and the reported aria-orientation. 'horizontal':
      ArrowLeft/ArrowRight. 'vertical': ArrowUp/ArrowDown. Both axes' arrows are accepted
      regardless.
    - ``children`` (ReactNode; required): Tab and TabMenu items to render inside the nav.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/TabList>.
    """

    def __init__(self, items: Iterable[Any], value: str, **props: Any) -> None:
        super().__init__("TabList", value=value, props={"items": _option_records(items), **props})


class SegmentedControl(Widget):
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
        JSON-safe SegmentedControl props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe SegmentedControl props forwarded to Astryx.

    Supported Astryx props include:

    - ``value`` (string; required): The currently selected value (controlled).
    - ``onChange`` ((value: string) => void; required): Callback fired when a segment is selected.
    - ``label`` (string; required): Accessible label for the radio group (used as aria-label, never
      rendered visually).
    - ``size`` ('sm' or 'md' or 'lg'): Size variant for the control.
    - ``layout`` ('hug' or 'fill'): Layout mode. hug (default) sizes segments to content; fill
      stretches them equally to fill the container.
    - ``isDisabled`` (boolean): Whether the entire control is disabled.
    - ``children`` (ReactNode; required): SegmentedControlItem children.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/SegmentedControl>.
    """

    def __init__(self, items: Iterable[Any], value: str, *, label: str, **props: Any) -> None:
        super().__init__("SegmentedControl", label=label, value=value, props={"items": _option_records(items), **props})


class RadioList(Widget):
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
        JSON-safe RadioList props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe RadioList props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for the radio group (always rendered for
      accessibility).
    - ``value`` (string; required): The currently selected value.
    - ``onChange`` ((value: string) => void; required): Callback fired when the selected value
      changes.
    - ``children`` (ReactNode; required): RadioListItem elements.
    - ``isLabelHidden`` (boolean): Whether to visually hide the label.
    - ``description`` (string): Description text displayed below the label.
    - ``orientation`` ('vertical' or 'horizontal'): Layout direction of the radio items.
    - ``isDisabled`` (boolean): Whether all radio items are disabled.
    - ``isRequired`` (boolean): Whether the radio group is required.
    - ``isOptional`` (boolean): Whether the field is optional (mutually exclusive with isRequired).
    - ``status`` (InputStatus): Status indicator ({ type, message }).
    - ``size`` ('sm' or 'md'): Size of the radio controls.
    - ``labelTooltip`` (string): Tooltip text for an info icon next to the label.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/RadioList>.
    """

    def __init__(self, items: Iterable[Any], value: str, *, label: str, **props: Any) -> None:
        super().__init__("RadioList", label=label, value=value, props={"items": _option_records(items), **props})


class CheckboxList(Widget):
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
        JSON-safe CheckboxList props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe CheckboxList props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for the checkbox group (always rendered for
      accessibility).
    - ``children`` (ReactNode; required): CheckboxListItem elements.
    - ``value`` (string[]): The currently selected values (collection mode).
    - ``onChange`` ((values: string[]) => void): Callback fired when the selected values change.
    - ``changeAction`` ((values: string[]) => void or Promise<void>): Async action on change with
      optimistic updates. While the promise is pending, the toggled item shows a spinner inside
      its checkbox and is marked aria-busy.
    - ``isLabelHidden`` (boolean): Whether to visually hide the label.
    - ``description`` (string): Description text displayed below the label.
    - ``density`` ('compact' or 'balanced' or 'spacious'): Spacing density for list items.
    - ``hasDividers`` (boolean): Whether to show dividers between items.
    - ``isDisabled`` (boolean): Whether all checkbox items are disabled.
    - ``status`` (InputStatus): Status indicator ({ type, message }).
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization. Must be a stylex.create()
      value.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/CheckboxList>.
    """

    def __init__(self, items: Iterable[Any], value: Iterable[str] = (), *, label: str, **props: Any) -> None:
        super().__init__("CheckboxList", label=label, value=list(value), props={"items": _option_records(items), **props})


class ButtonGroup(Widget):
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
        JSON-safe ButtonGroup props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe ButtonGroup props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Button or IconButton children.
    - ``label`` (string; required): Accessible group label used as aria-label.
    - ``orientation`` ('horizontal' or 'vertical'; default 'horizontal'): Button group orientation
      and keyboard navigation axis.
    - ``size`` ('sm' or 'md' or 'lg'; default 'md'): Default size for buttons in the group;
      individual buttons can override it.
    - ``isDisabled`` (boolean; default false): Disables all buttons in the group.
    - ``data-testid`` (string): Test selector for automated testing.
    - ``xstyle`` (StyleXStyles): StyleX styles for the group root.
    - ``className`` (string): CSS class names for the group root.
    - ``style`` (CSSProperties): Inline styles for the group root.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/ButtonGroup>.
    """

    def __init__(self, items: Iterable[Any], *, label: str, callbacks: Iterable[Callable[[ComponentWidget], None]] | None = None, **props: Any) -> None:
        super().__init__("ButtonGroup", label=label, callbacks=callbacks, props={"items": _option_records(items), "label": label, **props})


class AvatarGroup(Widget):
    """Render a compact group of Astryx avatars.

    Parameters
    ----------
    items : Iterable[Any]
        Item records used by generated child components or static search sources.
    overflow_count : int, default 0
        Number shown in the avatar-group overflow indicator.
    **props : Any
        JSON-safe AvatarGroup props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe AvatarGroup props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Avatar children, optionally followed by one
      AvatarGroupOverflow. Consumers handle slicing to the desired visible count.
    - ``size`` (AvatarSize): Size applied to all avatars via context.
    - ``ref`` (React.Ref<HTMLDivElement>): Ref forwarded to the root element.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization.
    - ``data-testid`` (string): Test selector for automated testing frameworks.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/AvatarGroup>.
    """

    def __init__(self, items: Iterable[Any], *, overflow_count: int = 0, **props: Any) -> None:
        super().__init__("AvatarGroup", props={"items": _option_records(items), "overflowCount": overflow_count, **props})


class Code(Widget):
    """Render inline code with Astryx styling.

    Parameters
    ----------
    code : str
        Astryx component option.
    **props : Any
        JSON-safe Code props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Code props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Code content.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization. Must be a stylex.create()
      value.
    - ``className`` (string): CSS class name for the root element. Prefer xstyle for styling.
    - ``style`` (CSSProperties): Inline styles. Prefer xstyle for StyleX-optimized styling.
    - ``data-testid`` (string): Test selector for automated testing frameworks.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Code>.
    """

    def __init__(self, code: str, **props: Any) -> None:
        super().__init__("Code", text=code, props=props)


class Citation(Widget):
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
        JSON-safe Citation props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Citation props forwarded to Astryx.

    Supported Astryx props include:

    - ``source`` (CitationSource; required): The citation source object containing title, url, and
      optional icon.
    - ``number`` (number; required): The display index for this citation.
    - ``variant`` ('label' or 'number'): Display style: a label chip showing the source title or a
      compact numbered badge.

    See Astryx component docs: <https://astryx.atmeta.com/components/Citation>.
    """

    def __init__(self, source: Mapping[str, Any], *, number: int = 1, variant: str = "number", **props: Any) -> None:
        super().__init__("Citation", value=number, variant=variant, props={"source": _clean_value(source), "number": number, "variant": variant, **props})


class Field(Widget):
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
        JSON-safe Field props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Field props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Label text for the field (always rendered for accessibility).
    - ``inputID`` (string; required): ID for the input element (used for the label htmlFor
      attribute).
    - ``children`` (ReactNode; required): The input or control to render.
    - ``isLabelHidden`` (boolean): Visually hide the label (still accessible to screen readers).
    - ``isDisabled`` (boolean): Whether the associated input is disabled. Propagates disabled
      styling to the label.
    - ``description`` (string): Description text displayed between the label and input.
    - ``descriptionID`` (string): ID for the description element (use for aria-describedby on the
      input).
    - ``isOptional`` (boolean): Whether the field is optional (mutually exclusive with isRequired).
    - ``isRequired`` (boolean): Whether the field is required (mutually exclusive with isOptional).
    - ``labelIcon`` (IconType): Icon to display before the label text. See 'npx astryx docs icons'
      for valid semantic names.
    - ``labelTooltip`` (string): Tooltip text to display in an info icon at the end of the label.
    - ``status`` (FieldStatus): Status indicator with type and optional message. When message is
      set, displays a colored status box.
    - ``statusVariant`` ('attached' or 'detached'): How the status message renders relative to the
      input. Attached overlaps the input border; detached floats below.
    - ``width`` (SizeValue): Width of the field (number = pixels, string used as-is, e.g. "100%").
      Sizes the whole field (label, control, and status) so they stay aligned. Prefer this over
      setting width via xstyle/className/style, which only size the inner control box.
    - ``ref`` (React.Ref<HTMLDivElement>): Ref forwarded to the root element.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.
    - ``className`` (string): CSS class name(s) appended to the root element. Prefer xstyle for
      StyleX deduplication.
    - ``style`` (React.CSSProperties): Inline styles applied to the root element. Takes priority
      over StyleX inline styles.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Field>.
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


class FieldStatus(Widget):
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
        JSON-safe FieldStatus props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe FieldStatus props forwarded to Astryx.

    Supported Astryx props include:

    - ``type`` ('error' or 'warning' or 'success'; required): Status type.
    - ``message`` (string; required): Status message text.
    - ``id`` (string): ID for aria-describedby association.
    - ``variant`` ('attached' or 'detached'): Visual variant: attached overlaps the input, detached
      floats below.

    See Astryx component docs: <https://astryx.atmeta.com/components/FieldStatus>.
    """

    def __init__(self, message: str, *, type: str = "success", variant: str = "detached", **props: Any) -> None:
        super().__init__("FieldStatus", label=message, variant=type, props={"type": type, "message": message, "variant": variant, **props})


class FormLayout(Widget):
    """Arrange Astryx form controls with consistent spacing.

    Parameters
    ----------
    children : ChildInput
        Child widget, sequence of widgets, or mapping of slot names to widgets.
    direction : str, default 'vertical'
        Layout direction.
    **props : Any
        JSON-safe FormLayout props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe FormLayout props forwarded to Astryx.

    Supported Astryx props include:

    - ``direction`` ('vertical' or 'horizontal' or 'horizontal-labels'): Controls field arrangement.
      Vertical stacks top-to-bottom, horizontal arranges left-to-right with equal flex-grow, and
      horizontal-labels uses CSS Grid with labels to the left of inputs (collapses to vertical
      on narrow viewports <=480px).
    - ``children`` (ReactNode): Form fields to arrange. Accepts Astryx inputs (TextInput, Selector,
      etc.) and Field-wrapped custom controls.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/FormLayout>.
    """

    def __init__(self, children: ChildInput = None, *, direction: str = "vertical", **props: Any) -> None:
        super().__init__("FormLayout", children, props={"direction": direction, **props})


class InputGroup(Widget):
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
        JSON-safe InputGroup props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe InputGroup props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Input and InputGroupText children.
    - ``label`` (string; required): Accessible label for the group.
    - ``isLabelHidden`` (boolean): Visually hide the label.
    - ``description`` (string): Helper text between label and input group.
    - ``isDisabled`` (boolean): Disable the entire group.
    - ``isOptional`` (boolean): Show "(optional)" indicator.
    - ``isRequired`` (boolean): Mark the field as required.
    - ``size`` ('sm' or 'md' or 'lg'): Default size for inputs in the group.
    - ``status`` (InputStatus): Status indicator applied to the group border.
    - ``labelTooltip`` (string): Tooltip text at the end of the label.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization.
    - ``data-testid`` (string): Test selector.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/InputGroup>.
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


class Collapsible(Widget):
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
        JSON-safe Collapsible props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Collapsible props forwarded to Astryx.

    Supported Astryx props include:

    - ``trigger`` (ReactNode; required): Content shown in the trigger area (always visible).
    - ``children`` (ReactNode): Content that collapses and expands.
    - ``defaultIsOpen`` (boolean): Default open state (uncontrolled).
    - ``isOpen`` (boolean): Controlled open state.
    - ``onOpenChange`` ((isOpen: boolean) => void): Callback invoked when the open state changes.
    - ``value`` (string): Identifier used for group coordination. Required when placed inside an
      CollapsibleGroup.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Collapsible>.
    """

    def __init__(self, children: ChildInput = None, *, trigger: str, default_open: bool = True, value: str = "", **props: Any) -> None:
        super().__init__(
            "Collapsible",
            children,
            label=trigger,
            props={"trigger": trigger, "defaultIsOpen": default_open, "value": value or None, **props},
        )


class Outline(Widget):
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
        JSON-safe Outline props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Outline props forwarded to Astryx.

    Supported Astryx props include:

    - ``items`` (OutlineItem[]; required): Ordered heading items to render as table-of-contents
      links.
    - ``activeId`` (string): Currently active item id. When provided, disables built-in scroll spy
      state ownership.
    - ``onActiveIdChange`` ((id: string) => void): Called when the active item changes from scroll
      spy or click.
    - ``label`` (string; default 'Table of contents'): Accessible label for the nav landmark.
    - ``density`` ('default' or 'compact'; default 'default'): Controls item padding density.
    - ``data-testid`` (string): Test selector for automated testing.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization.
    - ``className`` (string): CSS class names for the nav element.
    - ``style`` (CSSProperties): Inline styles for the nav element.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Outline>.
    """

    def __init__(self, items: Iterable[Mapping[str, Any]], *, active_id: str = "", label: str = "Table of contents", density: str = "compact", **props: Any) -> None:
        super().__init__(
            "Outline",
            label=label,
            value=active_id,
            props={"items": _clean_value(list(items)), "label": label, "density": density, **props},
        )


class TreeList(Widget):
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
        JSON-safe TreeList props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe TreeList props forwarded to Astryx.

    Supported Astryx props include:

    - ``items`` (TreeListItemData[]; required): Recursive tree item data; nested children arrays
      create hierarchy.
    - ``density`` ('compact' or 'balanced' or 'spacious'; default 'balanced'): Spacing density for
      tree list items.
    - ``header`` (ReactNode): Header content rendered above the tree and associated with
      aria-labelledby.
    - ``data-testid`` (string): Test selector for automated testing.
    - ``xstyle`` (StyleXStyles): StyleX styles for the root element.
    - ``className`` (string): CSS class names for the root element.
    - ``style`` (CSSProperties): Inline styles for the root element.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/TreeList>.
    """

    def __init__(self, items: Iterable[Mapping[str, Any]], *, header: str = "", density: str = "balanced", **props: Any) -> None:
        super().__init__("TreeList", props={"items": _clean_value(list(items)), "header": header or None, "density": density, **props})


class Toolbar(Widget):
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
        JSON-safe Toolbar props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Toolbar props forwarded to Astryx.

    Supported Astryx props include:

    - ``startContent`` (ReactNode): Content aligned to the start side.
    - ``centerContent`` (ReactNode): Content centered between start and end; switches layout to a
      three-column grid.
    - ``endContent`` (ReactNode): Content aligned to the end side.
    - ``label`` (string; required): Accessible label applied to the toolbar element.
    - ``size`` ('sm' or 'md' or 'lg'; default 'md'): Toolbar size cascaded to common child controls
      through SizeContext.
    - ``gap`` (spacing step; default 1): Gap between items within each slot.
    - ``orientation`` ('horizontal' or 'vertical'; default 'horizontal'): Keyboard navigation
      orientation.
    - ``variant`` (SectionVariant; default transparent): Visual variant passed through to the
      underlying Section.
    - ``dividers`` (array of 'top', 'bottom', 'start', or 'end'): Divider borders passed through to
      the underlying Section.
    - ``xstyle`` (StyleXStyles): StyleX styles for the Section root.
    - ``className`` (string): CSS class names for the Section root.
    - ``style`` (CSSProperties): Inline styles for the Section root.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Toolbar>.
    """

    def __init__(self, children: ChildInput = None, *, label: str, size: str = "sm", gap: int | float = 1, **props: Any) -> None:
        super().__init__("Toolbar", children, label=label, props={"label": label, "size": size, "gap": gap, **props})


class Tooltip(Widget):
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
        JSON-safe Tooltip props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Tooltip props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode): Trigger content. When anchorRef is provided, children may be
      omitted.
    - ``anchorRef`` (React.RefObject<HTMLElement>): External tooltip anchor used for sibling-mode
      rendering.
    - ``content`` (ReactNode; required): Tooltip content, typically short non-interactive text.
    - ``placement`` (LayerPlacement; default 'above'): Placement relative to the anchor.
    - ``alignment`` (LayerAlignment; default 'center'): Alignment along the placement axis.
    - ``delay`` (number; default 200): Delay in milliseconds before showing on hover.
    - ``hideDelay`` (number; default 0): Delay in milliseconds before hiding after mouse or focus
      leave.
    - ``focusTrigger`` ('auto' or 'always' or 'never'; default 'auto'): Controls whether focus opens
      the tooltip.
    - ``isEnabled`` (boolean; default true): Enables or disables hover and focus triggers.
    - ``onOpenChange`` ((isOpen: boolean) => void): Called when tooltip visibility changes.
    - ``hasHoverIndication`` ('auto' or boolean; default 'auto'): Controls dashed underline hover
      indication on the trigger.
    - ``isOpen`` (boolean): Controlled open state.
    - ``isDefaultOpen`` (boolean): Initial uncontrolled open state.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Tooltip>.
    """

    def __init__(self, content: str | ChildInput, trigger: ChildInput = None, *, label: str = "", **props: Any) -> None:
        children = {"trigger": trigger} if trigger is not None else None
        if not isinstance(content, str):
            children = {"trigger": trigger, "content": content} if trigger is not None else {"content": content}
            content_prop = None
        else:
            content_prop = content
        super().__init__("Tooltip", children, label=label or content_prop or "", props={"content": content_prop, **props})


class HoverCard(Widget):
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
        JSON-safe HoverCard props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe HoverCard props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Trigger content.
    - ``content`` (ReactNode; required): Interactive hover card content.
    - ``placement`` (LayerPlacement; default 'above'): Placement relative to the anchor.
    - ``alignment`` (LayerAlignment; default 'center'): Alignment along the placement axis.
    - ``delay`` (number; default 300): Delay in milliseconds before showing on hover.
    - ``hideDelay`` (number; default 200): Delay in milliseconds before hiding after mouse or focus
      leave.
    - ``focusTrigger`` ('auto' or 'always' or 'never'; default 'auto'): Controls whether focus opens
      the hover card.
    - ``isEnabled`` (boolean; default true): Enables or disables hover and focus triggers.
    - ``onOpenChange`` ((isOpen: boolean) => void): Called when hover card visibility changes.
    - ``hasHoverIndication`` ('auto' or boolean; default 'auto'): Controls dashed underline hover
      indication on the trigger.
    - ``isOpen`` (boolean): Controlled open state.
    - ``isDefaultOpen`` (boolean): Initial uncontrolled open state.
    - ``xstyle`` (StyleXStyles): StyleX styles for the hover card content.
    - ``className`` (string): CSS class names for the hover card content.
    - ``style`` (CSSProperties): Inline styles for the hover card content.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/HoverCard>.
    """

    def __init__(self, content: str | ChildInput, trigger: ChildInput, *, label: str = "", **props: Any) -> None:
        children = {"trigger": trigger}
        content_prop: str | None = content if isinstance(content, str) else None
        if not isinstance(content, str):
            children["content"] = content
        super().__init__("HoverCard", children, label=label or content_prop or "", props={"content": content_prop, **props})


class Popover(Widget):
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
        JSON-safe Popover props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Popover props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode or render function): Trigger content. Automatic mode requires a button
      or role=button descendant; render-function mode receives trigger props.
    - ``anchorRef`` (React.RefObject<HTMLElement>): External button or role=button anchor used for
      sibling-mode rendering.
    - ``content`` (ReactNode; required): Popover dialog content.
    - ``placement`` (LayerPlacement; default 'below'): Placement relative to the trigger.
    - ``alignment`` (LayerAlignment; default 'start'): Alignment along the placement axis.
    - ``isOpen`` (boolean): Controlled open state.
    - ``onOpenChange`` ((isOpen: boolean) => void): Called when popover visibility changes.
    - ``isEnabled`` (boolean; default true): Disables trigger interactions when false.
    - ``width`` (number or string; default 'auto'): Popover container width. Numbers are pixels;
      strings are CSS values.
    - ``label`` (string): Accessible label for the popover dialog.
    - ``hasCloseButton`` (boolean): Includes a hidden close button for keyboard users.
    - ``closeButtonLabel`` (string; default 'Close popover'): Accessible label for the hidden close
      button.
    - ``hasAutoFocus`` (boolean; default true): Auto-focuses the first focusable element when
      opened.
    - ``data-testid`` (string): Test selector for the popover container.
    - ``xstyle`` (StyleXStyles): StyleX styles for the popover content.
    - ``className`` (string): CSS class names for the popover content.
    - ``style`` (CSSProperties): Inline styles for the popover content.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Popover>.
    """

    def __init__(self, content: str | ChildInput, trigger: ChildInput, *, label: str, **props: Any) -> None:
        children = {"trigger": trigger}
        content_prop: str | None = content if isinstance(content, str) else None
        if not isinstance(content, str):
            children["content"] = content
        super().__init__("Popover", children, label=label, props={"content": content_prop, "label": label, **props})


class DropdownMenu(Widget):
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
        JSON-safe DropdownMenu props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe DropdownMenu props forwarded to Astryx.

    Supported Astryx props include:

    - ``button`` (DropdownMenuButtonProps): Props for the trigger button (Button props except
      onClick).
    - ``items`` (DropdownMenuOption[]; required): Array of menu entries. Each entry is one of: an
      action item '{label, onClick?, icon?, isDisabled?}', a divider '{type: "divider"}', or a
      section '{type: "section", title?, items: [...action items]}'.
    - ``isMenuOpen`` (boolean): Controlled open state for the menu.
    - ``onOpenChange`` ((isOpen: boolean) => void): Callback fired when the open state changes.
    - ``menuWidth`` (number or string): Custom menu width; defaults to matching the trigger button
      width.
    - ``onClick`` (() => void): Callback fired when the trigger button is clicked.
    - ``hasChevron`` (boolean): Whether to show a chevron icon on the trigger button. Set to false
      for icon-only triggers.
    - ``children`` ((item: DropdownMenuItemData) => ReactNode): Custom render function for each item
      in the list.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/DropdownMenu>.
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


class MoreMenu(Widget):
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
        JSON-safe MoreMenu props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe MoreMenu props forwarded to Astryx.

    Supported Astryx props include:

    - ``items`` (DropdownMenuOption[]; required): Menu items: data array of actions, dividers, and
      sections. Same type as DropdownMenu items prop.
    - ``label`` (string): Accessible label for the trigger button (aria-label) and tooltip text.
    - ``variant`` (ButtonVariant): Visual style variant of the trigger button.
    - ``size`` (ButtonSize): Size of the trigger button.
    - ``icon`` (ReactNode): Override the default three-dot icon. Accepts any ReactNode.
    - ``isDisabled`` (boolean): Whether the menu trigger is disabled.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/MoreMenu>.
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


class Calendar(Widget):
    """Render an Astryx calendar date picker.

    Parameters
    ----------
    value : str | Mapping[str, str] | None
        Synchronized component value.
    mode : str, default 'single'
        Component mode.
    **props : Any
        JSON-safe Calendar props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Calendar props forwarded to Astryx.

    Supported Astryx props include:

    - ``mode`` ('single' or 'range'): Selection mode.
    - ``value`` (ISODateString or DateRange): Controlled selected value.
    - ``defaultValue`` (ISODateString or DateRange): Uncontrolled default value.
    - ``onChange`` (Function): Selection callback.
    - ``numberOfMonths`` (1 or 2): Number of months to display.
    - ``min`` (ISODateString): Minimum selectable date.
    - ``max`` (ISODateString): Maximum selectable date.
    - ``dateConstraints`` (Array<(date: Date) => boolean>): Custom constraint functions.
    - ``focusDate`` (ISODateString): Controlled visible month.
    - ``onFocusDateChange`` ((focusDate: ISODateString) => void): Navigation callback.
    - ``handleRef`` (React.Ref<CalendarHandle>): Imperative handle for calendar navigation,
      including navigateTo().
    - ``hasOutsideDays`` (boolean): Show days from adjacent months.
    - ``hasWeekNumbers`` (boolean): Show ISO week numbers.
    - ``hasVariableRowCount`` (boolean): Variable vs fixed 6-row grid.
    - ``weekStartsOn`` (0 or 1 or 2 or 3 or 4 or 5 or 6 or 'sun' or 'mon' or 'tue' or 'wed' or 'thu'
      or 'fri' or 'sat'): First day of week. Accepts a number (0=Sunday) or a three-letter day
      name (e.g. "mon").

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Calendar>.
    """

    def __init__(self, value: str | Mapping[str, str] | None = None, *, mode: str = "single", **props: Any) -> None:
        super().__init__("Calendar", value=value, props={"mode": mode, **props})


class FileInput(Widget):
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
        JSON-safe FileInput props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe FileInput props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessible label for the file input.
    - ``value`` (File or File[] or null; required): Currently selected file(s). Controlled
      component.
    - ``onChange`` ((files: File or File[] or null) => void; required): Callback fired when files
      are selected or removed.
    - ``changeAction`` ((files: File or File[] or null) => Promise<void>): Async change action
      (React 19 transitions pattern). Use for immediate upload on file selection.
    - ``accept`` (string): Accepted file types. Uses the HTML accept attribute format (e.g.
      "image/*", ".pdf,.doc").
    - ``isMultiple`` (boolean): Whether multiple files can be selected. When true, value and
      onChange use File[] instead of File.
    - ``maxSize`` (number): Maximum file size in bytes. Files exceeding this are rejected with an
      error status.
    - ``maxFiles`` (number): Maximum number of files (only applies when isMultiple is true).
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible to screen
      readers.
    - ``description`` (string): Description text displayed between the label and input.
    - ``isOptional`` (boolean): Displays an "Optional" indicator next to the label. Mutually
      exclusive with isRequired.
    - ``isRequired`` (boolean): Displays a "Required" indicator next to the label and sets
      aria-required. Mutually exclusive with isOptional.
    - ``isDisabled`` (boolean): Disables the input, preventing interaction and dimming the element.
    - ``isLoading`` (boolean): Puts the input in a loading state, showing a spinner and setting
      aria-busy.
    - ``placeholder`` (string): Placeholder text shown when no file is selected.
    - ``mode`` ('input' or 'dropzone'): Visual mode. 'input' is a compact inline style; 'dropzone'
      is a larger area with drag-and-drop support.
    - ``status`` ({type: 'error' or 'warning' or 'success', message?: string}): Validation status:
      applies a colored border. If message is provided, displays a floating message below the
      input. Error type also sets aria-invalid.
    - ``labelTooltip`` (string): Tooltip text displayed in an info icon at the end of the label.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/FileInput>.

    Notes
    -----
    The synchronized value contains file metadata only; file bytes are not sent to Python."""

    def __init__(self, *, label: str, value: Any = None, multiple: bool = False, disabled: bool = False, **props: Any) -> None:
        super().__init__("FileInput", label=label, value=value, disabled=disabled, props={"label": label, "isMultiple": multiple, **props})


class Typeahead(Widget):
    """Render a notebook-safe Astryx typeahead.

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
    search : Callable[[str], Iterable[Any]] | None
        Optional Python-backed search source. The callback receives the current
        query string and returns item records, pairs, mappings, or strings that
        can be normalized into ``{"id": ..., "label": ...}`` records. When
        omitted, the frontend uses a static in-browser search source backed by
        ``items``.
    **props : Any
        JSON-safe Typeahead props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Typeahead props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessible label for the input.
    - ``searchSource`` (SearchSource<T>; required): Data source providing search and bootstrap
      methods for populating the dropdown.
    - ``value`` (T or null; required): Currently selected item, or null if nothing is selected.
    - ``onChange`` ((item: T or null) => void; required): Called when the selection changes.
    - ``placeholder`` (string): Input placeholder text.
    - ``hasEntriesOnFocus`` (boolean): Show bootstrap results on focus before typing.
    - ``hasClear`` (boolean): Show clear button to deselect the current value.
    - ``isDisabled`` (boolean): Disables the input.
    - ``maxMenuItems`` (number): Maximum number of dropdown items to display.
    - ``status`` (InputStatus): Validation status object with type and message for
      error/warning/success states.
    - ``renderItem`` ((item: T) => ReactNode): Custom render function for dropdown items. Default
      renders TypeaheadItem.
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible.
    - ``description`` (string): Helper text displayed below the label.
    - ``isRequired`` (boolean): Marks the field as required.
    - ``isOptional`` (boolean): Shows an optional indicator on the label.
    - ``labelTooltip`` (string): Tooltip text shown on the label.
    - ``emptySearchResultsText`` (string): Text shown when search returns no results.
    - ``hasAutoFocus`` (boolean): Auto-focus the input on mount.
    - ``size`` ('sm' or 'md' or 'lg'): Input and token size.
    - ``debounceMs`` (number): Debounce delay in ms before triggering search. Set to 0 for
      synchronous sources.
    - ``onChangeQuery`` ((query: string) => void): Callback fired when the search query text
      changes.
    - ``onOpenChange`` ((isOpen: boolean) => void): Callback when the dropdown opens or closes.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Typeahead>.

    Notes
    -----
    With ``search=None``, the frontend receives an Astryx ``createStaticSource``
    backed by ``items``. With a Python search callback, the frontend uses
    Astryx's async ``SearchSource`` interface and resolves each query through
    the anywidget comm channel. The selected item id is stored in ``value``."""

    def __init__(
        self,
        items: Iterable[Any] | Mapping[str, Any],
        value: str | None = None,
        *,
        label: str,
        disabled: bool = False,
        search: Callable[[str], Iterable[Any]] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Typeahead",
            label=label,
            value=value,
            disabled=disabled,
            search=search,
            props={"items": _search_records(items), "label": label, **props},
        )


class Tokenizer(Widget):
    """Render a notebook-safe Astryx tokenizer.

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
    search : Callable[[str], Iterable[Any]] | None
        Optional Python-backed search source. The callback receives the current
        query string and returns item records, pairs, mappings, or strings that
        can be normalized into ``{"id": ..., "label": ...}`` records. When
        omitted, the frontend uses a static in-browser search source backed by
        ``items``.
    **props : Any
        JSON-safe Tokenizer props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Tokenizer props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Accessible label for the input.
    - ``searchSource`` (SearchSource<T>; required): Data source providing search and bootstrap
      methods for populating the dropdown.
    - ``value`` (T[]; required): Array of currently selected items.
    - ``onChange`` ((items: T[], change: TokenizerChange<T>) => void; required): Called when
      selection changes. The change argument includes the affected item and type ('add' or
      'create' or 'remove' or 'reorder').
    - ``placeholder`` (string): Input placeholder text. Only shown when no tokens are selected.
    - ``maxEntries`` (number): Maximum number of selections allowed. Input is hidden when the limit
      is reached.
    - ``hasClear`` (boolean): Show a clear-all button for bulk removal of all tokens.
    - ``renderToken`` ((item: T, onRemove: () => void) => ReactNode): Custom render function for
      selected tokens. Default renders Token with label and onRemove.
    - ``renderItem`` ((item: T) => ReactNode): Custom render function for dropdown items. Default
      renders TypeaheadItem.
    - ``isDisabled`` (boolean): Disables the input and all token interactions.
    - ``status`` (InputStatus): Validation status object with type and message for
      error/warning/success states.
    - ``isLabelHidden`` (boolean): Visually hides the label while keeping it accessible.
    - ``description`` (string): Helper text displayed below the label.
    - ``isRequired`` (boolean): Marks the field as required.
    - ``isOptional`` (boolean): Shows an optional indicator on the label.
    - ``labelTooltip`` (string): Tooltip text shown on the label.
    - ``hasEntriesOnFocus`` (boolean): Show bootstrap results on focus before typing.
    - ``maxMenuItems`` (number): Maximum number of dropdown items to display.
    - ``emptySearchResultsText`` (string): Text shown when search returns no results.
    - ``hasAutoFocus`` (boolean): Auto-focus the input on mount.
    - ``size`` ('sm' or 'md' or 'lg'): Input and token size.
    - ``debounceMs`` (number): Debounce delay in ms before triggering search. Set to 0 for
      synchronous sources.
    - ``hasCreate`` (boolean): Allow users to create new tokens from free-text input. When true, a
      "Create" option appears in the dropdown for typed text that doesn't match existing
      results. The onChange change type is 'create' for these items.
    - ``onChangeQuery`` ((query: string) => void): Callback fired when the search query text
      changes.
    - ``endContent`` (ReactNode): Content to display at the end of the input row. Useful for
      buttons, result counts, or other controls.
    - ``handleRef`` (React.Ref<TokenizerHandle>): Imperative handle for focus() and blur() control.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value - not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Tokenizer>.

    Notes
    -----
    The wrapper stores selected ids in ``value`` rather than complete item
    records so notebook state remains compact and JSON-safe."""

    def __init__(
        self,
        items: Iterable[Any] | Mapping[str, Any],
        value: Iterable[str] = (),
        *,
        label: str,
        disabled: bool = False,
        search: Callable[[str], Iterable[Any]] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Tokenizer",
            label=label,
            value=list(value),
            disabled=disabled,
            search=search,
            props={"items": _search_records(items), "label": label, **props},
        )


class CommandPalette(Widget):
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
    search : Callable[[str], Iterable[Any]] | None, default None
        Optional Python search callback. When provided, Astryx search queries
        are sent to Python and callback results are normalized into
        ``{"id": ..., "label": ...}`` command records. When omitted, the
        frontend builds a static search source from ``items``.
    **props : Any
        JSON-safe CommandPalette props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe CommandPalette props forwarded to Astryx.

    Supported Astryx props include:

    - ``isOpen`` (boolean; required): Whether the command palette dialog is visible.
    - ``onOpenChange`` ((isOpen: boolean) => void; required): Called when the palette visibility
      changes.
    - ``searchSource`` (SearchSource<T>; required): Search source providing items via search(query)
      and bootstrap(). Use createStaticSource for static lists.
    - ``input`` (ReactNode): Input slot. Defaults to CommandPaletteInput with standard behavior.
    - ``footer`` (ReactNode): Footer slot. Defaults to CommandPaletteFooter showing keyboard hints.
    - ``renderItem`` ((item: T, isSelected: boolean) => ReactNode): Per-item render function.
      Auto-grouping by auxiliaryData.group is preserved. When omitted, renders label text.
    - ``emptySearchText`` (ReactNode): Content shown when a search query returns no results.
    - ``emptyBootstrapText`` (ReactNode): Content shown when there is no search query and
      bootstrap() returns nothing.
    - ``value`` (string): Controlled selected value for picker mode.
    - ``onValueChange`` ((value: string) => void): Called when the selected value changes in picker
      mode.
    - ``label`` (string): Accessible label for the command palette dialog.
    - ``width`` (number or string): Width of the dialog.
    - ``maxHeight`` (number or string): Maximum height of the dialog.
    - ``isInline`` (boolean): Renders command palette content inline without modal behavior.
      Automatically disables input auto-focus and initial highlighted-item auto-scroll. For
      documentation previews and showcases only.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/CommandPalette>.

    Notes
    -----
    The palette renders inline and open by default so it remains contained in a
    Jupyter output area instead of creating a page-level modal overlay."""

    def __init__(
        self,
        items: Iterable[Any] | Mapping[str, Any],
        value: str | None = None,
        *,
        label: str = "Command palette",
        search: Callable[[str], Iterable[Any]] | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "CommandPalette",
            label=label,
            value=value,
            search=search,
            props={"items": _search_records(items), "label": label, "isInline": True, **props},
        )


class Dialog(Widget):
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
        JSON-safe Dialog props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Dialog props forwarded to Astryx.

    Supported Astryx props include:

    - ``isOpen`` (boolean; required): Whether the dialog is open.
    - ``onOpenChange`` ((isOpen: boolean) => unknown; required): Callback when dialog visibility
      changes.
    - ``children`` (ReactNode; required): Dialog content.
    - ``width`` (number or string): Width of the dialog in pixels or any CSS value.
    - ``maxHeight`` (number or string): Maximum height of the dialog.
    - ``position`` (DialogPosition): Static position for the dialog; centered by default when
      omitted.
    - ``variant`` ('standard' or 'fullscreen'): Dialog variant: fullscreen expands to fill the
      entire viewport.
    - ``purpose`` ('required' or 'form' or 'info'): Controls dismissal behavior: required disables
      Escape and backdrop click; form disables backdrop click after interaction; info allows
      both.
    - ``isInline`` (boolean): Renders dialog content inline without the <dialog> element, backdrop,
      or modal behavior. For documentation previews and showcases only.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Dialog>.

    Notes
    -----
    The wrapper defaults to inline rendering to avoid modal focus-management
    conflicts inside Jupyter output areas. Set ``inline=False`` only when the
    surrounding notebook environment can safely host modal dialogs."""

    def __init__(self, children: ChildInput = None, *, open: bool = True, inline: bool = True, **props: Any) -> None:
        super().__init__("Dialog", children, value=open, props={"isInline": inline, **props})


class AlertDialog(Widget):
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
        JSON-safe AlertDialog props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe AlertDialog props forwarded to Astryx.

    Supported Astryx props include:

    - ``isOpen`` (boolean; required): Whether the dialog is open.
    - ``onOpenChange`` ((isOpen: boolean) => unknown; required): Visibility change callback.
    - ``title`` (string; required): Dialog title. Linked via aria-labelledby.
    - ``description`` (string; required): Consequence description. Linked via aria-describedby.
    - ``actionLabel`` (string; required): Action button label.
    - ``onAction`` (() => unknown; required): Called when action button is clicked. Does NOT
      auto-close.
    - ``cancelLabel`` (string): Cancel button label.
    - ``actionVariant`` (ButtonVariant): Action button variant.
    - ``isActionLoading`` (boolean): Shows loading spinner on the action button.
    - ``width`` (number or string): Dialog width.
    - ``isInline`` (boolean): Renders alert dialog content inline without modal behavior. For
      documentation previews and showcases only.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/AlertDialog>.

    Notes
    -----
    The wrapper defaults to inline rendering to avoid modal focus-management
    conflicts inside Jupyter output areas. The primary action emits a click
    message with ``action="confirm"``."""

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


# TODO(astryx): Follow-ups after notebook-safe wrappers:
# - evaluate non-inline Dialog/AlertDialog behavior once JupyterLab output focus
#   and layer interactions are well understood.


class Table(Widget):
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
        JSON-safe Table props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Table props forwarded to Astryx.

    Supported Astryx props include:

    - ``data`` (T[]): Array of data items to render as rows. T must extend Record<string, unknown>
      (use 'interface MyRow extends Record<string, unknown>' for custom types).
    - ``columns`` (TableColumn<T>[]): Column definitions: each column has {key, header, width?,
      align?, renderCell?}. The 'header' field sets the column heading text. If omitted, columns
      are auto-generated from data object keys.
    - ``idKey`` ((keyof T & string) or ((item: T) => string or number)): Row key for React
      reconciliation. Pass a property name string or a function. Falls back to row index if
      omitted.
    - ``density`` ('compact' or 'balanced' or 'spacious'): Row density controlling cell padding and
      font size.
    - ``dividers`` ('rows' or 'columns' or 'grid' or 'none'): Divider style rendered between cells.
    - ``isStriped`` (boolean): Applies a background wash to even-numbered rows.
    - ``hasHover`` (boolean): Applies a hover highlight background to rows on pointer devices.
    - ``verticalAlign`` ('middle' or 'top' or 'bottom'): Vertical alignment for body row cells.
      Controls 'vertical-align' on the '<td>' elements.
    - ``textOverflow`` ('wrap' or 'truncate'): How body cell text behaves when it exceeds the column
      width. 'wrap' lets text wrap and the row grow taller; 'truncate' clips with an ellipsis
      (default-rendered cells show a tooltip on hover when truncated). Header cells always
      truncate.
    - ``plugins`` (Record<string, TablePlugin<T>>): Named plugins that extend table behavior via the
      transform pipeline. Converted to an ordered array internally.
    - ``children`` (ReactNode): Children mode: render TableRow/TableCell directly instead of using
      data-driven rendering.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value: not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Table>.

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
        self._selection_callbacks: list[Callable[[Table], None]] = []
        self._sort_callbacks: list[Callable[[Table], None]] = []

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
        callback: Callable[[Table], None],
        remove: bool = False,
    ) -> None:
        """Register or unregister a callback for table selection changes."""
        if remove:
            self._selection_callbacks = [item for item in self._selection_callbacks if item is not callback]
            return
        self._selection_callbacks.append(callback)

    def on_sort(
        self,
        callback: Callable[[Table], None],
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


class EmptyState(Widget):
    """Render an Astryx empty-state message.

    Parameters
    ----------
    title : str
        Dialog or empty-state title.
    description : str, default ''
        Supporting description text.
    **props : Any
        JSON-safe EmptyState props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe EmptyState props forwarded to Astryx.

    Supported Astryx props include:

    - ``title`` (string; required): Primary message rendered as an <h3> heading inside the empty
      state.
    - ``description`` (string): Optional secondary text providing additional context below the
      title.
    - ``icon`` (ReactNode): Optional icon or illustration displayed above the title; rendered as
      decorative (aria-hidden="true").
    - ``actions`` (ReactNode): Optional action buttons displayed below the description, laid out
      horizontally by default and stacked vertically when isCompact is true.
    - ``headingLevel`` (1 or 2 or 3 or 4 or 5 or 6): Controls the rendered HTML heading tag (h1-h6)
      to fit the document outline.
    - ``isCompact`` (boolean): Enables the compact variant with reduced spacing for constrained
      content areas.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/EmptyState>.
    """

    def __init__(self, title: str, *, description: str = "", **props: Any) -> None:
        super().__init__("EmptyState", props={"title": title, "description": description, **props})


class Banner(Widget):
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
        JSON-safe Banner props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Banner props forwarded to Astryx.

    Supported Astryx props include:

    - ``status`` ('info' or 'warning' or 'error' or 'success'; required): Status type controlling
      icon and color.
    - ``title`` (ReactNode; required): Title text or ReactNode displayed in the header.
    - ``description`` (ReactNode): Description text rendered below the title in the header.
    - ``icon`` (ReactNode): Override the default status icon.
    - ``isDismissable`` (boolean): Whether the banner can be dismissed by the user.
    - ``onDismiss`` (() => void): Called when the dismiss button is clicked; banner hides itself
      regardless of whether this is provided.
    - ``endContent`` (ReactNode): Action content rendered in the header area, end-aligned. Typically
      a button or link.
    - ``container`` ('card' or 'section'): Container type: card has border-radius; section is
      full-width with no border-radius for page-level use.
    - ``children`` (ReactNode): Content rendered in the card-background area below the colored
      header.
    - ``defaultIsExpanded`` (boolean): Whether the content area (children) starts expanded. Only
      relevant when children are provided.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Banner>.
    """

    def __init__(self, title: str, *, status: str = "info", description: str = "", **props: Any) -> None:
        super().__init__("Banner", label=title, props={"title": title, "status": status, "description": description, **props})


class StatusDot(Widget):
    """Render an inline Astryx status indicator.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    variant : str, default 'neutral'
        Astryx visual variant.
    **props : Any
        JSON-safe StatusDot props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe StatusDot props forwarded to Astryx.

    Supported Astryx props include:

    - ``variant`` ('success' or 'warning' or 'error' or 'accent' or 'neutral'; required): Semantic
      color variant.
    - ``label`` (string; required): Accessible label surfaced via aria-label.
    - ``isPulsing`` (boolean): Enables a pulse animation; respects prefers-reduced-motion: reduce.
    - ``tooltip`` (string): Tooltip text shown on hover to explain the status meaning.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/StatusDot>.
    """

    def __init__(self, label: str, *, variant: str = "neutral", **props: Any) -> None:
        super().__init__("StatusDot", label=label, variant=variant, props=props)


class ProgressBar(Widget):
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
        JSON-safe ProgressBar props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe ProgressBar props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): accessible label
    - ``value`` (number): Current value (ignored when indeterminate).
    - ``max`` (number): Maximum value.
    - ``isLabelHidden`` (boolean): Visually hide the label (remains accessible).
    - ``hasValueLabel`` (boolean): Show formatted value text (ignored when indeterminate).
    - ``formatValueLabel`` ((value: number, max: number) => string): Custom value label formatter;
      defaults to a percentage string.
    - ``variant`` ('accent' or 'success' or 'warning' or 'error' or 'neutral'): Semantic color
      variant.
    - ``isIndeterminate`` (boolean): Animated loading indicator for unknown progress.
    - ``isDisabled`` (boolean): Visually disabled state: grays out the fill and text. Use for
      canceled or inactive operations.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/ProgressBar>.
    """

    def __init__(self, value: int | float = 0, *, label: str, variant: str = "accent", **props: Any) -> None:
        super().__init__("ProgressBar", label=label, value=value, variant=variant, props=props)


class Spinner(Widget):
    """Render an Astryx loading spinner.

    Parameters
    ----------
    label : str, default 'Loading'
        Visible or accessible label for the component.
    **props : Any
        JSON-safe Spinner props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Spinner props forwarded to Astryx.

    Supported Astryx props include:

    - ``size`` ('sm' or 'md' or 'lg'): Spinner size (10px, 14px, 18px).
    - ``shade`` ('default' or 'onMedia' or 'subtle' or 'inherit'): Color shade for light or dark
      backgrounds.
    - ``label`` (ReactNode): Visible content below the spinner. String labels auto-set aria-label.
    - ``aria-label`` (string): Accessible name for screen readers. Defaults to label (if string) or
      "Loading".
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Spinner>.
    """

    def __init__(self, *, label: str = "Loading", **props: Any) -> None:
        super().__init__("Spinner", label=label, props={"label": label, **props})


class Skeleton(Widget):
    """Render an Astryx skeleton placeholder.

    Parameters
    ----------
    width : int | str, default '100%'
        CSS width. Numbers are normalized by anylumino where supported.
    height : int | str, default 16
        CSS height. Numbers are normalized by anylumino where supported.
    **props : Any
        JSON-safe Skeleton props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Skeleton props forwarded to Astryx.

    Supported Astryx props include:

    - ``width`` (number or string): Width in pixels (number) or CSS value (string).
    - ``height`` (number or string): Height in pixels (number) or CSS value (string).
    - ``radius`` ('none' or 0 or 1 or 2 or 3 or 4 or 'rounded'): Border radius using design token
      scale. Use none for sharp corners, rounded for fully rounded (avatars, pills, circles).
    - ``index`` (number): Index for staggered animation timing. For element at index n, animation
      starts at DELAY_TIME + (STAGGER_TIME x n).

    See Astryx component docs: <https://astryx.atmeta.com/components/Skeleton>.
    """

    def __init__(self, *, width: int | str = "100%", height: int | str = 16, **props: Any) -> None:
        super().__init__("Skeleton", props={"width": width, "height": height, **props})


class Token(Widget):
    """Render an Astryx token or chip.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    color : str, default 'default'
        Astryx component option.
    **props : Any
        JSON-safe Token props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Token props forwarded to Astryx.

    Supported Astryx props include:

    - ``label`` (string; required): Text label displayed inside the token.
    - ``size`` ('sm' or 'md' or 'lg'): The size of the token.
    - ``color`` ('default' or 'red' or 'orange' or 'yellow' or 'green' or 'teal' or 'cyan' or 'blue'
      or 'purple' or 'pink' or 'gray'): Color variant of the token.
    - ``icon`` (ReactNode): Optional icon rendered before the label.
    - ``isDisabled`` (boolean): Whether the token is disabled; reduces opacity and blocks
      interactions.
    - ``onRemove`` ((e: React.MouseEvent) => void): Callback fired when the remove button is
      clicked. When provided, an X button is rendered inside the token.
    - ``onClick`` ((e: React.MouseEvent) => void): Click handler. When provided, the token renders
      as a <span> container with an invisible <button> inside for accessibility.
    - ``href`` (string): Link URL. When provided, the token renders as an <a> element.
    - ``description`` (string): Accessible description applied via aria-description on the root
      element.
    - ``endContent`` (ReactNode): Content rendered after the label and before the remove button.
    - ``isLabelHidden`` (boolean): Visually hides the label using a screen-reader-only clip
      technique; the label remains accessible.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Token>.
    """

    def __init__(self, label: str, *, color: str = "default", **props: Any) -> None:
        super().__init__("Token", label=label, props={"color": color, **props})


class Kbd(Widget):
    """Render keyboard shortcut text with Astryx styling.

    Parameters
    ----------
    keys : str
        Keyboard shortcut text.
    **props : Any
        JSON-safe Kbd props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Kbd props forwarded to Astryx.

    Supported Astryx props include:

    - ``keys`` (string; required): Keyboard shortcut string. Use "+" to separate keys. Special keys:
      mod (Cmd on Mac), ctrl, alt, shift, enter, backspace, escape, tab, up, down, left, right.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.
    - ``className`` (string): CSS class name for the root element. Prefer xstyle for styling;
      className is provided for integration with non-StyleX systems.
    - ``style`` (CSSProperties): Inline styles for the root element. Prefer xstyle for styling;
      inline styles bypass StyleX optimization.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Kbd>.
    """

    def __init__(self, keys: str, **props: Any) -> None:
        super().__init__("Kbd", props={"keys": keys, **props})


class Link(Widget):
    """Render an Astryx text link.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    href : str, default ''
        Link destination URL.
    **props : Any
        JSON-safe Link props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Link props forwarded to Astryx.

    Supported Astryx props include:

    - ``as`` (LinkComponentType): Custom component to render instead of an anchor when href is
      provided.
    - ``label`` (string): Accessible label when the visible content is not self-descriptive.
    - ``href`` (string): Link destination. When omitted, Astryx renders a button styled as a link.
    - ``hasUnderline`` (boolean; default false): Always shows underline; otherwise underline appears
      on hover.
    - ``isDisabled`` (boolean; default false): Disables the link.
    - ``isExternalLink`` (boolean; default false): Opens in a new tab, adds an external icon, and
      sets safe target/rel defaults.
    - ``newTabLabel`` (string; default '(opens in new tab)'): Screen-reader text appended to
      external links.
    - ``target`` (string): Where to open the linked document; overridden to _blank when
      isExternalLink is true.
    - ``rel`` (string): Link relationship; automatically includes noopener noreferrer for external
      links.
    - ``download`` (string or boolean): Requests browser download and optionally supplies a
      filename.
    - ``referrerPolicy`` (HTMLAttributeReferrerPolicy): Referrer policy for the link.
    - ``onClick`` (MouseEventHandler): Click handler before navigation, or primary action when href
      is omitted.
    - ``tooltip`` (string): Tooltip text shown on hover.
    - ``isStandalone`` (boolean; default false): Applies base font sizing for non-inline links.
    - ``type`` (TextType; default 'body'): Semantic Text type forwarded to the internal Text
      component.
    - ``size`` (TextSize): Explicit font size override forwarded to Text.
    - ``weight`` (TextWeight): Font weight override forwarded to Text.
    - ``color`` (TextColor; default 'accent'): Text color forwarded to Text.
    - ``display`` (TextDisplay; default 'inline'): Display type forwarded to Text.
    - ``maxLines`` (number; default 0): Maximum lines before truncation.
    - ``children`` (ReactNode; required): Link content.
    - ``xstyle`` (StyleXStyles): StyleX styles for the root element.
    - ``className`` (string): CSS class names for the root element.
    - ``style`` (CSSProperties): Inline styles for the root element.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Link>.
    """

    def __init__(self, label: str, *, href: str = "", **props: Any) -> None:
        super().__init__("Link", text=label, label=label, props={"href": href or None, **props})


class Avatar(Widget):
    """Render an Astryx avatar.

    Parameters
    ----------
    name : str
        Astryx component option.
    **props : Any
        JSON-safe Avatar props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Avatar props forwarded to Astryx.

    Supported Astryx props include:

    - ``src`` (string): Primary image source URL.
    - ``fallbackSrc`` (string): Fallback image when primary fails.
    - ``name`` (string): User name for initials and alt text.
    - ``alt`` (string): Alt text (falls back to name).
    - ``size`` (AvatarSize): Avatar size (named or numeric pixel value).
    - ``status`` (ReactNode): Corner content for status indicators.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Avatar>.
    """

    def __init__(self, name: str, **props: Any) -> None:
        super().__init__("Avatar", label=name, props={"name": name, **props})


class Icon(Widget):
    """Render an Astryx icon by name.

    Parameters
    ----------
    icon : str
        Astryx icon name.
    **props : Any
        JSON-safe Icon props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Icon props forwarded to Astryx.

    Supported Astryx props include:

    - ``icon`` (IconName or ComponentType<SVGProps>; required): Semantic icon name or SVG component.
      Valid semantic names: close, chevronDown, chevronLeft, chevronRight, check, success,
      error, warning, info, calendar, clock, externalLink, menu, moreHorizontal, search,
      arrowUp, arrowDown, arrowsUpDown, funnel, eyeSlash, viewColumns, copy, checkDouble,
      wrench, stop, microphone. For any icon not in this list, pass an SVG component directly
      (e.g. import from lucide-react or @heroicons/react). Note: this prop is called 'icon', not
      'name'.
    - ``color`` ('primary' or 'secondary' or 'tertiary' or 'disabled' or 'accent' or 'success' or
      'error' or 'warning' or 'inherit'): Color variant mapped to Astryx icon color tokens.
    - ``size`` ('xsm' or 'sm' or 'md' or 'lg'): Icon size.

    See Astryx component docs: <https://astryx.atmeta.com/components/Icon>.
    """

    def __init__(self, icon: str, **props: Any) -> None:
        super().__init__("Icon", text=icon, icon=icon, props={"icon": icon, **props})


class Thumbnail(Widget):
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
        JSON-safe Thumbnail props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Thumbnail props forwarded to Astryx.

    Supported Astryx props include:

    - ``src`` (string): Image source URL.
    - ``alt`` (string): Alt text for the image.
    - ``label`` (string): Accessible label (e.g. file name). Shown as tooltip on hover.
    - ``onRemove`` ((e: React.MouseEvent) => void): Callback for the overlaid remove button.
    - ``onClick`` ((e: React.MouseEvent) => void): Click handler. Adds button semantics and hover
      shadow.
    - ``isLoading`` (boolean): Shows skeleton (no src) or upload overlay (with src).
    - ``isDisabled`` (boolean): Whether the thumbnail is disabled.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.
    - ``className`` (string): CSS class name for the root element. Prefer xstyle for styling;
      className is provided for integration with non-StyleX systems.
    - ``style`` (CSSProperties): Inline styles for the root element. Prefer xstyle for styling;
      inline styles bypass StyleX optimization.
    - ``data-testid`` (string): Test selector for automated testing frameworks.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Thumbnail>.
    """

    def __init__(self, *, label: str = "", src: str = "", alt: str = "", **props: Any) -> None:
        super().__init__("Thumbnail", label=label, props={"src": src or None, "alt": alt or label, "label": label, **props})


class CodeBlock(Widget):
    """Render syntax-highlighted code with Astryx styling.

    Parameters
    ----------
    code : str
        Astryx component option.
    language : str, default 'python'
        Code language used for syntax highlighting.
    **props : Any
        JSON-safe CodeBlock props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe CodeBlock props forwarded to Astryx.

    Supported Astryx props include:

    - ``code`` (string; required): The code string to display.
    - ``language`` (string): Language for syntax highlighting. Use "plaintext" to disable.
    - ``title`` (string): Filename or label shown in the header bar.
    - ``hasLanguageLabel`` (boolean): Show the language name in the header bar. Hidden when language
      is "plaintext".
    - ``hasLineNumbers`` (boolean): Show a line number gutter.
    - ``highlightLines`` (number[]): 1-indexed line numbers to highlight.
    - ``hasCopyButton`` (boolean): Show a copy-to-clipboard button.
    - ``onCopy`` (() => void): Callback after the code is copied.
    - ``isWrapped`` (boolean): Wrap long lines instead of enabling horizontal scroll.
    - ``maxHeight`` (number or string): Max height before the block scrolls vertically.
    - ``size`` ('sm' or 'md'): Text size variant.
    - ``width`` (string): Width of the code block. Any CSS width value. 'fit-content' (default)
      shrinks to longest line. '100%' fills parent width.
    - ``container`` ('card' or 'section'): Container presentation style. 'card' (default): border
      and radius with the muted syntax background for a standalone card look. 'section': no
      border or radius and a transparent background so the block blends into the card or panel
      it's embedded in.
    - ``tokenizer`` ((code: string, language: string) => Array<{type: string; start: number; end:
      number}>): Custom tokenizer override for unsupported languages.
    - ``isCollapsible`` (boolean): Allow collapsing the code body into just the header bar. Starts
      expanded; the header becomes clickable to toggle. Only shows the toggle when the code
      exceeds collapsibleThreshold lines.
    - ``collapsibleThreshold`` (number): Minimum number of lines before the collapse toggle appears.
      Below this threshold the code block renders normally even when isCollapsible is true.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization. Must be a stylex.create()
      value.
    - ``className`` (string): CSS class name for the root element. Prefer xstyle for styling.
    - ``style`` (CSSProperties): Inline styles. Prefer xstyle for StyleX-optimized styling.
    - ``data-testid`` (string): Test selector for automated testing frameworks.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/CodeBlock>.
    """

    def __init__(self, code: str, *, language: str = "python", **props: Any) -> None:
        super().__init__("CodeBlock", props={"code": code, "language": language, **props})


class Markdown(Widget):
    """Render Markdown content through Astryx.

    Parameters
    ----------
    text : str
        Text content synchronized to the frontend component.
    **props : Any
        JSON-safe Markdown props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Markdown props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (string; required): The markdown string to render.
    - ``display`` ('block' or 'inline'): Display type. Markdown defaults to block. Use 'inline' for
      markdown spans embedded inside text.
    - ``density`` ('default' or 'compact'): Controls spacing between block-level elements.
    - ``headingLevelStart`` (1 or 2 or 3 or 4 or 5 or 6): The HTML heading level that markdown #
      maps to. Shifts all heading levels down to fit the surrounding page hierarchy. Levels
      exceeding h6 are clamped to h6.
    - ``isStreaming`` (boolean): Enables streaming mode; it uses incremental parsing and a smooth
      fade-in animation for chunk-by-chunk text delivery.
    - ``onLinkClick`` ((href: string, event: MouseEvent) => void or false): Handler for link clicks.
      Return false to prevent the default navigation behavior.
    - ``sources`` (Record<string, MarkdownSource>): Citation sources keyed by ID. When provided,
      [id] and [id] markers in the markdown that match a key are rendered as citation chips.
    - ``citationStyle`` ('label' or 'number'): How citations are displayed inline. 'label' shows a
      chip with source title, icon, and border. 'number' shows a compact numbered badge.
    - ``contentWidth`` (number or string): Max width for prose content (paragraphs, headings, lists,
      blockquotes). Tables and code blocks are unconstrained and can expand to the full
      container width. Use for readable line lengths in wide layouts.
    - ``contentAlign`` ('start' or 'center'): Alignment of prose content within the container when
      contentWidth is narrower than the available space.
    - ``inlinePlugins`` (MarkdownInlinePlugin[]): Transforms regex matches in parsed text nodes into
      custom inline React elements. Use for issue refs, diff refs, mentions, and other shorthand
      patterns. Inline code and fenced code blocks are unaffected.
    - ``autolink`` ('gfm'): Opt-in autolinking of bare URLs and emails. 'gfm' applies
      GitHub-Flavored Markdown autolink-literal rules: bare https?://..., www...., <scheme:url>,
      <email>, and user@host all become links. Trailing sentence punctuation and unbalanced
      trailing close-parens are excluded; matches inside code spans, code blocks, existing
      links, and image alt text are skipped. Default behavior (option unset) is unchanged.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.
    - ``className`` (string): CSS class name for the root element. Prefer xstyle for styling;
      className is provided for integration with non-StyleX systems.
    - ``style`` (CSSProperties): Inline styles for the root element. Prefer xstyle for styling;
      inline styles bypass StyleX optimization.
    - ``data-testid`` (string): Test selector for automated testing frameworks.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Markdown>.
    """

    def __init__(self, text: str, **props: Any) -> None:
        super().__init__("Markdown", text=text, props=props)


class Blockquote(Widget):
    """Render quoted text with Astryx blockquote styling.

    Parameters
    ----------
    text : str
        Text content synchronized to the frontend component.
    **props : Any
        JSON-safe Blockquote props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Blockquote props forwarded to Astryx.

    Supported Astryx props include:

    - ``children`` (ReactNode; required): Content of the blockquote.
    - ``cite`` (ReactNode): Optional attribution for the quote. Rendered in a <footer> with <cite>.
    - ``xstyle`` (StyleXStyles): StyleX styles for layout customization (margins, positioning,
      sizing). Must be a stylex.create() value, not an inline style object like style={{}}.

    Props typed as React nodes, render functions, event handlers, refs, or StyleX styles are
    documented for Astryx parity but cannot be serialized directly from Python unless the
    wrapper adapts them.

    See Astryx component docs: <https://astryx.atmeta.com/components/Blockquote>.
    """

    def __init__(self, text: str, **props: Any) -> None:
        super().__init__("Blockquote", text=text, props=props)


class Timestamp(Widget):
    """Render a timestamp value with Astryx formatting.

    Parameters
    ----------
    value : str | int | float
        Synchronized component value.
    **props : Any
        JSON-safe Timestamp props forwarded to Astryx. See the ``Astryx Props`` section below.

    Astryx Props
    ------------
    JSON-safe Timestamp props forwarded to Astryx.

    Supported Astryx props include:

    - ``value`` (string or number; required): The date/time to display. Accepts Unix timestamps
      (seconds) or ISO 8601 strings.
    - ``format`` ('relative' or 'auto' or 'date' or 'date_time' or 'time' or 'system_date' or
      'system_date_time' or 'system_time'): Display format. 'relative' shows '2 hours ago',
      'date' shows 'Mar 21, 2025', 'date_time' shows 'Mar 21, 2025, 2:51 PM', 'time' shows '2:51
      PM', 'system_*' variants use ISO-style formatting, 'auto' switches from relative to
      date_time based on recency.
    - ``autoThreshold`` (number): Threshold in seconds for 'auto' format to switch from relative to
      date_time.
    - ``hasTooltip`` (boolean): Whether to show a tooltip with the full date/time on hover when
      displaying relative time.
    - ``isTimezoneShown`` (boolean): Whether to append the timezone abbreviation. Applies to
      date_time, time, system_date_time, and system_time formats.
    - ``isLive`` (boolean): Whether the relative time should update live (e.g. "2 min ago" -> "3 min
      ago").
    - ``type`` (TextType): Semantic text type from Text. Determines size, weight, and line-height.
    - ``size`` (TextSize): Explicit font size override. Overrides the size from type.
    - ``color`` (TextColor): Text color.
    - ``weight`` (TextWeight): Font weight override.

    See Astryx component docs: <https://astryx.atmeta.com/components/Timestamp>.
    """

    def __init__(self, value: str | int | float, **props: Any) -> None:
        super().__init__("Timestamp", value=value, props=props)


__all__ = [
    "AspectRatio",
    "AlertDialog",
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
    "Checkbox",
    "CheckboxList",
    "ClickableCard",
    "Citation",
    "Code",
    "CodeBlock",
    "CommandPalette",
    "Component",
    "Collapsible",
    "DropdownMenu",
    "DateInput",
    "DateRangeInput",
    "DateTimeInput",
    "Dialog",
    "Divider",
    "EmptyState",
    "Field",
    "FieldStatus",
    "FileInput",
    "FormLayout",
    "Grid",
    "HoverCard",
    "Heading",
    "Icon",
    "IconButton",
    "InputGroup",
    "Kbd",
    "Link",
    "List",
    "Markdown",
    "MetadataList",
    "MoreMenu",
    "MultiSelector",
    "NumberInput",
    "Outline",
    "ProgressBar",
    "Popover",
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
    "TabList",
    "Table",
    "Text",
    "TextArea",
    "TextInput",
    "Theme",
    "Thumbnail",
    "TimeInput",
    "Timestamp",
    "ToggleButton",
    "Token",
    "Tokenizer",
    "Toolbar",
    "Tooltip",
    "TreeList",
    "Typeahead",
    "Widget",
    "Brand",
    "BuiltTheme",
]
