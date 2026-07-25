"""Astryx data-display and feedback widgets."""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any

import traitlets as t

from ..components import ComponentWidget
from .base import Widget
from .base import _clean_props
from .base import _clean_value
from .base import _named_props
from .base import _table_columns
from .base import _table_rows


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
    density : str | None, default None
        Compact, balanced, or spacious row density.
    dividers : str | None, default None
        Row, column, grid, or no divider treatment.
    striped : bool | None, default None
        Whether alternating rows receive a background wash.
    hover : bool | None, default None
        Whether rows highlight on pointer hover.
    vertical_align : str | None, default None
        Body-cell vertical alignment.
    text_overflow : str | None, default None
        Wrap or truncate overflowing cell text.
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
        density: str | None = None,
        dividers: str | None = None,
        striped: bool | None = None,
        hover: bool | None = None,
        vertical_align: str | None = None,
        text_overflow: str | None = None,
        **props: Any,
    ) -> None:
        row_list = list(rows)
        column_list = _table_columns(columns, row_list)
        self._row_key = row_key or "__row_id"
        super().__init__(
            "Table",
            props=_named_props(
                props,
                rows=_table_rows(row_list, column_list, self._row_key),
                columns=column_list,
                idKey=self._row_key,
                density=density,
                dividers=dividers,
                isStriped=striped,
                hasHover=hover,
                verticalAlign=vertical_align,
                textOverflow=text_overflow,
            ),
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
        column_list = (
            _table_columns(columns, row_list)
            if columns is not None or not self.columns
            else self.columns
        )
        self._set_table_props(
            rows=_table_rows(row_list, column_list, self._row_key),
            columns=column_list,
            idKey=self._row_key,
        )
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
            self._selection_callbacks = [
                item for item in self._selection_callbacks if item is not callback
            ]
            return
        self._selection_callbacks.append(callback)

    def on_sort(
        self,
        callback: Callable[[Table], None],
        remove: bool = False,
    ) -> None:
        """Register or unregister a callback for table sort changes."""
        if remove:
            self._sort_callbacks = [
                item for item in self._sort_callbacks if item is not callback
            ]
            return
        self._sort_callbacks.append(callback)

    def _normalize_new_row(
        self, row: Any, row_key: str | None = None
    ) -> dict[str, Any]:
        if row_key is not None:
            self._row_key = row_key or "__row_id"
            self._set_table_props(idKey=self._row_key)
        columns = self.columns
        if not columns:
            columns = _table_columns(None, [row])
            self._set_table_props(columns=columns)
        normalized = _table_rows([row], columns, self._row_key)[0]
        if row_key is None and self._row_key == "__row_id":
            existing_values = {
                str(existing.get(self._row_key)) for existing in self.rows
            }
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
            source = (
                values.get("cells")
                if isinstance(values.get("cells"), Mapping)
                else values
            )
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

    def _handle_frontend_message(
        self, _widget: object, content: dict[str, Any], _buffers: object
    ) -> None:
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
    heading_level : int | None, default None
        Semantic heading level.
    compact : bool | None, default None
        Whether to use reduced spacing.
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

    def __init__(
        self,
        title: str,
        *,
        description: str = "",
        heading_level: int | None = None,
        compact: bool | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "EmptyState",
            props=_named_props(
                props,
                title=title,
                description=description,
                headingLevel=heading_level,
                isCompact=compact,
            ),
        )


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
    dismissable : bool | None, default None
        Whether the user can dismiss the banner.
    container : str | None, default None
        Card or section container presentation.
    expanded : bool | None, default None
        Whether child content starts expanded.
    action_callbacks : Iterable[Callable[[ComponentWidget, Any], None]] | None
        Python callbacks receiving the ``"dismiss"`` action identifier.
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

    def __init__(
        self,
        title: str,
        *,
        status: str = "info",
        description: str = "",
        dismissable: bool | None = None,
        container: str | None = None,
        expanded: bool | None = None,
        action_callbacks: Iterable[Callable[[ComponentWidget, Any], None]]
        | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Banner",
            label=title,
            action_callbacks=action_callbacks,
            props=_named_props(
                props,
                title=title,
                status=status,
                description=description,
                isDismissable=dismissable,
                container=container,
                defaultIsExpanded=expanded,
            ),
        )


class Pagination(Widget):
    """Page through a data set with an Astryx pagination control.

    ``value`` holds the current one-based page. When ``page_size_options`` is
    given, choosing a new page size arrives through ``on_action`` rather than
    ``value``, so the page number stays the synchronized state.

    Parameters
    ----------
    page : int, default 1
        Current one-based page, synchronized as ``value``.
    total_items : int | None, default None
        Total row count, used to derive the page count.
    total_pages : int | None, default None
        Explicit page count when the total row count is unknown.
    page_size : int | None, default None
        Rows per page.
    page_size_options : Iterable[int] | None, default None
        Selectable page sizes. Selecting one fires ``on_action``.
    more : bool | None, default None
        Whether more pages exist, for cursor-style paging.
    sibling_count : int | None, default None
        Page buttons shown either side of the current page.
    variant : str, default ''
        Astryx visual variant.
    size : str | None, default None
        Control size.
    label : str, default ''
        Accessible label for the control.
    disabled : bool, default False
        Whether the component should render disabled.
    **props : Any
        JSON-safe Pagination props forwarded to Astryx.

    See Astryx component docs: <https://astryx.atmeta.com/components/Pagination>.
    """

    def __init__(
        self,
        page: int = 1,
        *,
        total_items: int | None = None,
        total_pages: int | None = None,
        page_size: int | None = None,
        page_size_options: Iterable[int] | None = None,
        more: bool | None = None,
        sibling_count: int | None = None,
        variant: str = "",
        size: str | None = None,
        label: str = "",
        disabled: bool = False,
        **props: Any,
    ) -> None:
        super().__init__(
            "Pagination",
            value=page,
            label=label,
            variant=variant,
            disabled=disabled,
            props=_named_props(
                props,
                totalItems=total_items,
                totalPages=total_pages,
                pageSize=page_size,
                pageSizeOptions=list(page_size_options)
                if page_size_options is not None
                else None,
                hasMore=more,
                siblingCount=sibling_count,
                size=size,
            ),
        )


class StatusDot(Widget):
    """Render an inline Astryx status indicator.

    Astryx renders a fixed 8px dot and surfaces ``label`` as ``aria-label``, so
    the label never appears as visible text. Pair the dot with a ``Text``
    widget in a horizontal ``Stack`` when the status needs a visible caption.

    Parameters
    ----------
    label : str
        Accessible label describing the status. Screen readers announce it; it
        is not rendered as visible text.
    variant : str, default 'neutral'
        Astryx visual variant.
    pulsing : bool | None, default None
        Whether to animate the status dot.
    tooltip : str | None, default None
        Hover explanation for the status.
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

    def __init__(
        self,
        label: str,
        *,
        variant: str = "neutral",
        pulsing: bool | None = None,
        tooltip: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "StatusDot",
            label=label,
            variant=variant,
            props=_named_props(props, isPulsing=pulsing, tooltip=tooltip),
        )


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
    max : int | float | None, default None
        Maximum progress value.
    label_hidden : bool | None, default None
        Whether to visually hide the accessible label.
    value_label : bool | None, default None
        Whether to display the formatted value.
    indeterminate : bool | None, default None
        Whether progress is unknown.
    disabled : bool, default False
        Whether to render the inactive visual state.
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

    def __init__(
        self,
        value: int | float = 0,
        *,
        label: str,
        variant: str = "accent",
        max: int | float | None = None,
        label_hidden: bool | None = None,
        value_label: bool | None = None,
        indeterminate: bool | None = None,
        disabled: bool = False,
        **props: Any,
    ) -> None:
        super().__init__(
            "ProgressBar",
            label=label,
            value=value,
            variant=variant,
            disabled=disabled,
            props=_named_props(
                props,
                max=max,
                isLabelHidden=label_hidden,
                hasValueLabel=value_label,
                isIndeterminate=indeterminate,
            ),
        )


class Spinner(Widget):
    """Render an Astryx loading spinner.

    Parameters
    ----------
    label : str, default 'Loading'
        Visible or accessible label for the component.
    size : str | None, default None
        Spinner size.
    shade : str | None, default None
        Spinner color treatment for its background.
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

    def __init__(
        self,
        *,
        label: str = "Loading",
        size: str | None = None,
        shade: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Spinner",
            label=label,
            props=_named_props(
                props, label=label, size=size, shade=shade, **{"aria-label": label}
            ),
        )


class Skeleton(Widget):
    """Render an Astryx skeleton placeholder.

    Parameters
    ----------
    width : int | str, default '100%'
        CSS width. Numbers are normalized by anylumino where supported.
    height : int | str, default 16
        CSS height. Numbers are normalized by anylumino where supported.
    radius : str | int | None, default None
        Skeleton corner radius.
    index : int | None, default None
        Staggered animation index.
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

    def __init__(
        self,
        *,
        width: int | str = "100%",
        height: int | str = 16,
        radius: str | int | None = None,
        index: int | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Skeleton",
            width=width,
            height=height,
            props=_named_props(
                props, width=width, height=height, radius=radius, index=index
            ),
        )


class Token(Widget):
    """Render an Astryx token or chip.

    Parameters
    ----------
    label : str
        Visible or accessible label for the component.
    color : str, default 'default'
        Astryx component option.
    size : str | None, default None
        Token size.
    disabled : bool, default False
        Whether the token is disabled.
    href : str | None, default None
        Optional link destination.
    description : str | None, default None
        Accessible description.
    label_hidden : bool | None, default None
        Whether to visually hide the label.
    removable : bool, default False
        Whether to show the remove control.
    clickable : bool, default False
        Whether the token acts as a button.
    action_callbacks : Iterable[Callable[[ComponentWidget, Any], None]] | None
        Python callbacks receiving ``"remove"`` or ``"click"``.
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

    def __init__(
        self,
        label: str,
        *,
        color: str = "default",
        size: str | None = None,
        disabled: bool = False,
        href: str | None = None,
        description: str | None = None,
        label_hidden: bool | None = None,
        removable: bool = False,
        clickable: bool = False,
        action_callbacks: Iterable[Callable[[ComponentWidget, Any], None]]
        | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Token",
            label=label,
            disabled=disabled,
            action_callbacks=action_callbacks,
            props=_named_props(
                props,
                color=color,
                size=size,
                isDisabled=disabled,
                href=href,
                description=description,
                isLabelHidden=label_hidden,
                onRemove=removable,
                clickable=clickable,
            ),
        )


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
    underline : bool | None, default None
        Whether the underline is always visible.
    disabled : bool, default False
        Whether the link is disabled.
    external : bool | None, default None
        Whether to use external-link behavior.
    target : str | None, default None
        Browser navigation target.
    tooltip : str | None, default None
        Hover tooltip text.
    standalone : bool | None, default None
        Whether to apply standalone text sizing.
    text_type : str | None, default None
        Semantic text type.
    size : str | None, default None
        Explicit text-size override.
    weight : str | None, default None
        Font-weight override.
    color : str | None, default None
        Theme text color.
    max_lines : int | None, default None
        Maximum rendered lines before truncation.
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

    def __init__(
        self,
        label: str,
        *,
        href: str = "",
        underline: bool | None = None,
        disabled: bool = False,
        external: bool | None = None,
        target: str | None = None,
        tooltip: str | None = None,
        standalone: bool | None = None,
        text_type: str | None = None,
        size: str | None = None,
        weight: str | None = None,
        color: str | None = None,
        max_lines: int | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Link",
            text=label,
            label=label,
            disabled=disabled,
            props=_named_props(
                props,
                href=href or None,
                hasUnderline=underline,
                isDisabled=disabled,
                isExternalLink=external,
                target=target,
                tooltip=tooltip,
                isStandalone=standalone,
                type=text_type,
                size=size,
                weight=weight,
                color=color,
                maxLines=max_lines,
            ),
        )


class Avatar(Widget):
    """Render an Astryx avatar.

    Parameters
    ----------
    name : str
        Astryx component option.
    src : str | None, default None
        Primary image URL.
    fallback_src : str | None, default None
        Fallback image URL.
    alt : str | None, default None
        Alternative image text.
    size : str | int | None, default None
        Named or pixel avatar size.
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

    def __init__(
        self,
        name: str,
        *,
        src: str | None = None,
        fallback_src: str | None = None,
        alt: str | None = None,
        size: str | int | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Avatar",
            label=name,
            props=_named_props(
                props,
                name=name,
                src=src,
                fallbackSrc=fallback_src,
                alt=alt,
                size=size,
            ),
        )


class Icon(Widget):
    """Render an Astryx icon by name.

    Parameters
    ----------
    icon : str
        Astryx icon name.
    color : str | None, default None
        Theme icon color.
    size : str | None, default None
        Icon size.
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

    def __init__(
        self,
        icon: str,
        *,
        color: str | None = None,
        size: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Icon",
            text=icon,
            icon=icon,
            props=_named_props(props, icon=icon, color=color, size=size),
        )


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
    loading : bool | None, default None
        Whether to show the loading presentation.
    disabled : bool, default False
        Whether interaction is disabled.
    removable : bool, default False
        Whether to show the remove control.
    clickable : bool, default False
        Whether the thumbnail acts as a button.
    action_callbacks : Iterable[Callable[[ComponentWidget, Any], None]] | None
        Python callbacks receiving ``"remove"`` or ``"click"``.
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

    def __init__(
        self,
        *,
        label: str = "",
        src: str = "",
        alt: str = "",
        loading: bool | None = None,
        disabled: bool = False,
        removable: bool = False,
        clickable: bool = False,
        action_callbacks: Iterable[Callable[[ComponentWidget, Any], None]]
        | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Thumbnail",
            label=label,
            disabled=disabled,
            action_callbacks=action_callbacks,
            props=_named_props(
                props,
                src=src or None,
                alt=alt or label,
                label=label,
                isLoading=loading,
                isDisabled=disabled,
                onRemove=removable,
                clickable=clickable,
            ),
        )


class CodeBlock(Widget):
    """Render syntax-highlighted code with Astryx styling.

    Parameters
    ----------
    code : str
        Astryx component option.
    language : str, default 'python'
        Code language used for syntax highlighting.
    title : str | None, default None
        Header filename or label.
    language_label : bool | None, default None
        Whether to show the language in the header.
    line_numbers : bool | None, default None
        Whether to show the line-number gutter.
    highlight_lines : Iterable[int] | None, default None
        One-indexed lines to highlight.
    copy_button : bool | None, default None
        Whether to show the copy control.
    wrapped : bool | None, default None
        Whether long lines wrap instead of scrolling.
    max_height : int | float | str | None, default None
        Maximum height before vertical scrolling.
    size : str | None, default None
        Code text size.
    width : str | None, default None
        CSS width of the code block.
    container : str | None, default None
        Card or section presentation.
    collapsible : bool | None, default None
        Whether long code can collapse.
    collapsible_threshold : int | None, default None
        Minimum line count for the collapse control.
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

    def __init__(
        self,
        code: str,
        *,
        language: str = "python",
        title: str | None = None,
        language_label: bool | None = None,
        line_numbers: bool | None = None,
        highlight_lines: Iterable[int] | None = None,
        copy_button: bool | None = None,
        wrapped: bool | None = None,
        max_height: int | float | str | None = None,
        size: str | None = None,
        width: str | None = None,
        container: str | None = None,
        collapsible: bool | None = None,
        collapsible_threshold: int | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "CodeBlock",
            width=width,
            props=_named_props(
                props,
                code=code,
                language=language,
                title=title,
                hasLanguageLabel=language_label,
                hasLineNumbers=line_numbers,
                highlightLines=list(highlight_lines)
                if highlight_lines is not None
                else None,
                hasCopyButton=copy_button,
                isWrapped=wrapped,
                maxHeight=max_height,
                size=size,
                width=width,
                container=container,
                isCollapsible=collapsible,
                collapsibleThreshold=collapsible_threshold,
            ),
        )


class Markdown(Widget):
    """Render Markdown content through Astryx.

    Parameters
    ----------
    text : str
        Text content synchronized to the frontend component.
    display : str | None, default None
        Block or inline display.
    density : str | None, default None
        Default or compact block spacing.
    heading_level_start : int | None, default None
        Heading level corresponding to Markdown ``#``.
    streaming : bool | None, default None
        Whether to use incremental streaming presentation.
    sources : Mapping[str, Any] | None, default None
        Citation sources keyed by identifier.
    citation_style : str | None, default None
        Label or numeric citations.
    content_width : int | float | str | None, default None
        Maximum prose width.
    content_align : str | None, default None
        Prose alignment inside the available width.
    autolink : str | None, default None
        Optional GFM bare-link handling.
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

    def __init__(
        self,
        text: str,
        *,
        display: str | None = None,
        density: str | None = None,
        heading_level_start: int | None = None,
        streaming: bool | None = None,
        sources: Mapping[str, Any] | None = None,
        citation_style: str | None = None,
        content_width: int | float | str | None = None,
        content_align: str | None = None,
        autolink: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Markdown",
            text=text,
            props=_named_props(
                props,
                display=display,
                density=density,
                headingLevelStart=heading_level_start,
                isStreaming=streaming,
                sources=sources,
                citationStyle=citation_style,
                contentWidth=content_width,
                contentAlign=content_align,
                autolink=autolink,
            ),
        )


class Blockquote(Widget):
    """Render quoted text with Astryx blockquote styling.

    Parameters
    ----------
    text : str
        Text content synchronized to the frontend component.
    cite : str | None, default None
        Optional quote attribution.
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

    def __init__(self, text: str, *, cite: str | None = None, **props: Any) -> None:
        super().__init__("Blockquote", text=text, props=_named_props(props, cite=cite))


class Timestamp(Widget):
    """Render a timestamp value with Astryx formatting.

    Parameters
    ----------
    value : str | int | float
        Synchronized component value.
    format : str | None, default None
        Relative, automatic, date, time, or system display format.
    auto_threshold : int | float | None, default None
        Automatic-format threshold in seconds.
    tooltip : bool | None, default None
        Whether relative timestamps show the full value on hover.
    timezone : bool | None, default None
        Whether to append the timezone abbreviation.
    live : bool | None, default None
        Whether relative text updates over time.
    text_type : str | None, default None
        Semantic text type.
    size : str | None, default None
        Explicit text-size override.
    color : str | None, default None
        Theme text color.
    weight : str | None, default None
        Font-weight override.
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

    def __init__(
        self,
        value: str | int | float,
        *,
        format: str | None = None,
        auto_threshold: int | float | None = None,
        tooltip: bool | None = None,
        timezone: bool | None = None,
        live: bool | None = None,
        text_type: str | None = None,
        size: str | None = None,
        color: str | None = None,
        weight: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(
            "Timestamp",
            value=value,
            props=_named_props(
                props,
                format=format,
                autoThreshold=auto_threshold,
                hasTooltip=tooltip,
                isTimezoneShown=timezone,
                isLive=live,
                type=text_type,
                size=size,
                color=color,
                weight=weight,
            ),
        )
