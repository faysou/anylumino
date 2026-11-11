"""A virtualized data grid built on Tabulator, with rows held in Python.

The kernel owns the rows and a revision counter. Each view asks for a snapshot
when it renders and then applies the row changes the kernel sends, so a grid
takes updates at tick rate without resending every row. A view that misses a
revision asks for a new snapshot.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

import traitlets as t

from .common import ActivationCallbacks
from .common import SharedBundleWidget
from .common import json_value
from .common import static_asset
from .enums import Transport
from .enums import choice
from .layout import _size_to_css


SNAPSHOT = "tabulator-snapshot"
DELTA = "tabulator-delta"
EDIT = "tabulator-edit"
SELECT = "tabulator-select"
ROW_CLICK = "tabulator-row-click"

# The wire form of a `JsCode`: an object whose only key is this one.
FUNCTION_KEY = "$js"

# Constructor options that have their own `Tabulator` arguments.
RESERVED_OPTIONS = ("data", "columns", "index")


class DeltaOp(StrEnum):
    """The row change a delta message carries."""

    UPDATE = "update"
    ADD = "add"
    UPSERT = "upsert"
    DELETE = "delete"


@dataclass(frozen=True)
class JsCode:
    """JavaScript function source that Tabulator receives as a function.

    Use it wherever Tabulator takes a function, such as a column formatter,
    sorter, editor, validator, mutator, or menu action. The source runs in the
    notebook page. A mapping whose only key is ``"$js"``, with the source as its
    value, means the same.

    Examples
    --------
    ```python
    al.JsCode("function(cell) { return cell.getValue().toFixed(2); }")
    ```

    Parameters
    ----------
    source : str
        A JavaScript expression that evaluates to a function.
    """

    source: str


@dataclass(frozen=True)
class CellEdit:
    """A cell edit made in a `Tabulator` view.

    Parameters
    ----------
    row_id : Any
        The edited row's value under the table's ``index`` field.
    field : str
        The edited column's field.
    value : Any
        The new value.
    old_value : Any
        The value before the edit.
    """

    row_id: Any
    field: str
    value: Any
    old_value: Any


SelectCallback = Callable[["Tabulator"], None]
EditCallback = Callable[["Tabulator", CellEdit], None]


class Tabulator(ActivationCallbacks, SharedBundleWidget):
    """Virtualized data grid built on Tabulator 6.7.

    ``columns`` and ``options`` take Tabulator's own names, so the
    [Tabulator documentation](https://tabulator.info/docs/6.7) applies to them.
    Wherever Tabulator takes a function, pass a `JsCode`.

    Python holds the rows. ``update_rows``, ``add_rows``, ``upsert_rows``, and
    ``delete_rows`` change them and send only the changed rows to the browser;
    assigning ``data`` replaces every row. Every row carries a unique value
    under the ``index`` field.

    ``on_select`` callbacks run when the user changes the selection, which
    needs Tabulator's ``selectableRows`` option. ``on_edit`` callbacks run
    with a `CellEdit` when the user edits a cell, which needs an ``editor`` on
    the column. ``on_click`` callbacks run when the user clicks a row, and
    ``on_action`` callbacks also receive the row mapping.

    Examples
    --------
    ```python
    al.Tabulator(
        [
            {"id": 1, "symbol": "ESZ6", "last": 5012.25, "qty": 3},
            {"id": 2, "symbol": "NQZ6", "last": 18011.5, "qty": -1},
        ],
        [
            {"title": "Symbol", "field": "symbol"},
            {"title": "Last", "field": "last", "hozAlign": "right"},
            {"title": "Qty", "field": "qty", "editor": "number"},
        ],
        options={"selectableRows": 1},
        height=160,
    )
    ```

    Parameters
    ----------
    data : Any, default None
        Rows: an iterable of mappings, an object with ``to_dict("records")``
        such as a pandas DataFrame, or an object with ``__arrow_c_stream__``
        such as a polars DataFrame, which needs ``pyarrow``.
    columns : Iterable[Mapping[str, Any]] | None, default None
        Tabulator column definitions. Without them the grid shows one column
        per row field.
    index : str, default 'id'
        Row id field. When no row has it, rows get the ids ``0, 1, 2, ...``.
    options : Mapping[str, Any] | None, default None
        Other Tabulator constructor options, such as ``layout`` or
        ``selectableRows``. ``data``, ``columns``, and ``index`` have their own
        arguments.
    selected : Iterable[Any], default ()
        Index values of the initially selected rows.
    transport : Transport | str, default 'auto'
        How rows reach the browser. ``"auto"`` sends Arrow IPC for columnar
        input when ``pyarrow`` imports, and JSON otherwise.
    width : int | float | str | None, default None
        CSS width; ``"100%"`` when omitted. Inside a layout panel the grid
        fills its slot instead, as for ``height``.
    height : int | float | str | None, default None
        CSS height; ``"320px"`` when omitted. The grid needs a bounded height
        to render only its visible rows. Inside a layout panel the grid fills
        its slot instead, except in a scroll box or a ``fit_content`` panel.
    callbacks : Iterable[Callable[[Tabulator], None]] | None, default None
        Row click callbacks.
    action_callbacks : Iterable[Callable[[Tabulator, Any], None]] | None, default None
        Row click callbacks that receive the row mapping.
    """

    _esm = static_asset("tabulator/tabulator_widget.loader.js")
    _bundle = static_asset("tabulator/tabulator_widget.bundle.js")
    _css = static_asset("tabulator/tabulator_widget.bundle.css")

    columns = t.List(t.Any(), default_value=[]).tag(sync=True, to_json=lambda value, _widget: _wire(value))
    options = t.Dict(default_value={}).tag(sync=True, to_json=lambda value, _widget: _wire(value))
    index = t.Unicode("id").tag(sync=True)
    selected = t.List(t.Any(), default_value=[]).tag(sync=True)
    width = t.Unicode("100%").tag(sync=True)
    height = t.Unicode("320px").tag(sync=True)

    def __init__(
        self,
        data: Any = None,
        columns: Iterable[Mapping[str, Any]] | None = None,
        *,
        index: str = "id",
        options: Mapping[str, Any] | None = None,
        selected: Iterable[Any] = (),
        transport: Transport | str = Transport.AUTO,
        width: int | float | str | None = None,
        height: int | float | str | None = None,
        callbacks: Iterable[Callable[[Tabulator], None]] | None = None,
        action_callbacks: Iterable[Callable[[Tabulator, Any], None]] | None = None,
        **kwargs: Any,
    ) -> None:
        self._transport = choice(transport, Transport, "transport")
        if self._transport == Transport.ARROW:
            _require_arrow()

        self._index = index
        self._revision = 0
        self._load(data)
        self._init_callbacks()
        self._select_callbacks: list[SelectCallback] = []
        self._edit_callbacks: list[EditCallback] = []
        super().__init__(
            columns=list(columns or []),
            options=dict(options or {}),
            index=index,
            selected=list(selected),
            width=_size_to_css(width, "100%"),
            height=_size_to_css(height, "320px"),
            **kwargs,
        )
        self.on_msg(self._handle_message)
        self._register_callbacks(callbacks, action_callbacks)

    @property
    def data(self) -> list[dict[str, Any]]:
        """Copies of the current rows, in insertion order.

        Cell values are stored as the browser receives them: dates, times, and
        datetimes become ISO 8601 strings, and NaN becomes `None`. Assigning
        rows replaces every row in every view, keeping each view's sort and
        scroll position.
        """

        return [dict(row) for row in self._row_map().values()]

    @data.setter
    def data(self, data: Any) -> None:
        self._load(data)
        self._revision += 1
        self._send_snapshot()
        self.selected = list(self.selected)

    @property
    def revision(self) -> int:
        """Number of row changes so far; every snapshot and delta carries it."""

        return self._revision

    def update_rows(self, rows: Iterable[Mapping[str, Any]]) -> None:
        """Update existing rows by index value, merging the given fields.

        Raises
        ------
        ValueError
            If a row lacks the ``index`` field.
        KeyError
            If no row has a given index value. Nothing changes in either case.
        """
        updates = [self._row(row) for row in rows]
        current = self._row_map()
        for row in updates:
            if row[self._index] not in current:
                raise KeyError(f"table row not found: {row[self._index]!r}")

        if not updates:
            return

        for row in updates:
            current[row[self._index]].update(row)
        self._send_delta(DeltaOp.UPDATE, rows=updates)

    def add_rows(self, rows: Any, *, top: bool = False) -> None:
        """Append rows, or prepend them with ``top=True``.

        ``rows`` takes the same forms as ``data``. When the table assigned its
        own ids, rows without the ``index`` field continue them.

        Raises
        ------
        ValueError
            If an index value is missing from some rows or already taken.
        """
        current = self._row_map()
        added, source = self._parse(rows, existing=current)
        if not added:
            return

        self._rows = {**added, **current} if top else {**current, **added}
        if source is not None and self._use_arrow():
            self._send_delta(DeltaOp.ADD, top=top, arrow=source)
        else:
            self._send_delta(DeltaOp.ADD, rows=list(added.values()), top=top)

    def upsert_rows(self, rows: Iterable[Mapping[str, Any]]) -> None:
        """Update rows whose index value exists and append the others.

        Raises
        ------
        ValueError
            If a row lacks the ``index`` field.
        """
        changes = [self._row(row) for row in rows]
        if not changes:
            return

        current = self._row_map()
        for row in changes:
            key = row[self._index]
            if key in current:
                current[key].update(row)
            else:
                current[key] = dict(row)
        self._send_delta(DeltaOp.UPSERT, rows=changes)

    def delete_rows(self, ids: Iterable[Any]) -> None:
        """Delete rows by index value and drop them from ``selected``.

        Raises
        ------
        KeyError
            If no row has a given index value; nothing changes.
        """
        keys = list(dict.fromkeys(_cell(key) for key in ids))
        current = self._row_map()
        for key in keys:
            if key not in current:
                raise KeyError(f"table row not found: {key!r}")

        if not keys:
            return

        for key in keys:
            del current[key]
        self._send_delta(DeltaOp.DELETE, ids=keys)
        if any(key in keys for key in self.selected):
            self.selected = [key for key in self.selected if key not in keys]

    def on_select(self, callback: SelectCallback, remove: bool = False) -> None:
        """Register or unregister a callback for selection changes made in a view."""
        if remove:
            self._select_callbacks = [item for item in self._select_callbacks if item is not callback]

            return

        self._select_callbacks.append(callback)

    def on_edit(self, callback: EditCallback, remove: bool = False) -> None:
        """Register or unregister a callback for cell edits made in a view."""
        if remove:
            self._edit_callbacks = [item for item in self._edit_callbacks if item is not callback]

            return

        self._edit_callbacks.append(callback)

    @t.validate("columns")
    def _function_columns(self, proposal: dict[str, Any]) -> list[Any]:
        columns = _functions(list(proposal["value"]))
        if not all(isinstance(column, Mapping) for column in columns):
            raise t.TraitError("columns must be Tabulator column definitions, one mapping per column")

        return columns

    @t.validate("options")
    def _function_options(self, proposal: dict[str, Any]) -> dict[str, Any]:
        reserved = [name for name in RESERVED_OPTIONS if name in proposal["value"]]
        if reserved:
            raise t.TraitError(f"options cannot set {', '.join(reserved)}; use the Tabulator argument of that name")

        return _functions(dict(proposal["value"]))

    @t.validate("index")
    def _rekey(self, proposal: dict[str, Any]) -> str:
        index = proposal["value"]
        if index == self._index:
            return index

        rows = list(self._row_map().values())
        if rows and not all(index in row for row in rows):
            raise t.TraitError(f"index={index!r}: every row needs this field")

        keyed: dict[Any, dict[str, Any]] = {}
        for row in rows:
            if row[index] in keyed:
                raise t.TraitError(f"index={index!r}: duplicate value {row[index]!r}")

            keyed[row[index]] = row
        self._index = index
        self._rows = keyed
        self._next_id = None
        # Selected values belong to the old index field.
        self.selected = []

        return index

    @t.validate("selected")
    def _known_selection(self, proposal: dict[str, Any]) -> list[Any]:
        values = [_cell(value) for value in proposal["value"]]
        if not values:
            return values

        rows = self._row_map()

        return [value for value in values if value in rows]

    def _load(self, data: Any) -> None:
        self._next_id: int | None = None
        self._columnar = _is_columnar(data)
        # A columnar load keeps only its Arrow table; `_row_map` builds the
        # mappings when a read or change first needs them, and the table stays
        # the snapshot until a change.
        self._rows: dict[Any, dict[str, Any]] | None
        self._source: Any
        self._rows, self._source = self._parse(data, existing=None)

    # Returns the rows of `data` keyed by index value, and their Arrow table when
    # `data` is columnar and pyarrow imports. `existing` holds the current rows
    # when `data` is added to them, or is None for a full load, which returns
    # no mappings for a columnar `data`.
    def _parse(self, data: Any, existing: Mapping[Any, Any] | None) -> tuple[dict[Any, dict[str, Any]] | None, Any]:
        arrow = _arrow()
        if data is None:
            return {}, None

        if arrow is not None and _is_columnar(data):
            table = self._keyed_table(arrow, _wire_table(arrow, _arrow_table(arrow, data)), existing)
            if existing is None:
                _check_index_column(arrow, table, self._index)

                return None, table

            return self._keyed(_table_rows(table), existing), table

        if hasattr(data, "to_dict"):
            data = data.to_dict("records")
        elif hasattr(data, "__arrow_c_stream__"):
            raise ImportError("rows from an Arrow stream need pyarrow; install it or pass row mappings")

        rows = []
        for row in data:
            if not isinstance(row, Mapping):
                raise TypeError(f"rows must be mappings, got {type(row).__name__}")

            rows.append({str(name): _cell(value) for name, value in row.items()})

        return self._keyed(self._assign_ids(rows, existing), existing), None

    def _assign_ids(self, rows: list[dict[str, Any]], existing: Mapping[Any, Any] | None) -> list[dict[str, Any]]:
        if not rows or any(self._index in row for row in rows):
            return rows

        start = self._first_new_id(existing, len(rows))

        return [{**row, self._index: start + offset} for offset, row in enumerate(rows)]

    def _first_new_id(self, existing: Mapping[Any, Any] | None, count: int) -> int:
        if existing is None:
            start = 0
        elif self._next_id is None:
            raise ValueError(f"rows need the index field {self._index!r}")
        else:
            start = self._next_id
        self._next_id = start + count

        return start

    def _keyed(self, rows: list[dict[str, Any]], existing: Mapping[Any, Any] | None) -> dict[Any, dict[str, Any]]:
        if not all(self._index in row for row in rows):
            raise ValueError(f"index field {self._index!r} is missing from some rows")

        keyed: dict[Any, dict[str, Any]] = {}
        for row in rows:
            key = row[self._index]
            if key in keyed or (existing is not None and key in existing):
                raise ValueError(f"duplicate index value {key!r} in field {self._index!r}")

            keyed[key] = row

        return keyed

    def _keyed_table(self, arrow: Any, table: Any, existing: Mapping[Any, Any] | None) -> Any:
        if table.num_rows == 0 or self._index in table.column_names:
            return table

        start = self._first_new_id(existing, table.num_rows)

        return table.append_column(self._index, arrow.array(range(start, start + table.num_rows), arrow.int64()))

    def _row(self, row: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(row, Mapping):
            raise TypeError(f"rows must be mappings, got {type(row).__name__}")

        normalized = {str(name): _cell(value) for name, value in row.items()}
        if self._index not in normalized:
            raise ValueError(f"row lacks the index field {self._index!r}: {normalized!r}")

        return normalized

    def _row_map(self) -> dict[Any, dict[str, Any]]:
        if self._rows is None:
            self._rows = {row[self._index]: row for row in _table_rows(self._source)}

        return self._rows

    def _use_arrow(self) -> bool:
        if self._transport == Transport.JSON:
            return False

        if self._transport == Transport.ARROW:
            return True

        return self._columnar and _arrow() is not None

    def _snapshot_table(self) -> Any:
        if not self._use_arrow():
            return None

        if self._source is not None:
            return self._source

        arrow = _require_arrow()
        try:
            return arrow.Table.from_pylist(list(self._row_map().values()))
        except (arrow.ArrowException, TypeError):
            # Mixed cell types after edits do not fit one Arrow column type.
            if self._transport == Transport.ARROW:
                raise

            return None

    def _send_snapshot(self) -> None:
        content: dict[str, Any] = {"type": SNAPSHOT, "revision": self._revision}
        table = self._snapshot_table()
        if table is None:
            content["rows"] = list(self._row_map().values())
            self.send(content)

            return

        content["format"] = "arrow"
        self.send(content, [_ipc(_require_arrow(), table)])

    def _send_delta(
        self,
        op: DeltaOp,
        *,
        rows: list[dict[str, Any]] | None = None,
        ids: list[Any] | None = None,
        top: bool = False,
        arrow: Any = None,
        origin: str | None = None,
    ) -> None:
        self._source = None
        self._revision += 1
        content: dict[str, Any] = {"type": DELTA, "revision": self._revision, "op": op.value, "origin": origin}
        if op == DeltaOp.ADD:
            content["top"] = top
        if ids is not None:
            content["ids"] = ids
        if arrow is not None:
            content["format"] = "arrow"
            self.send(content, [_ipc(_require_arrow(), arrow)])

            return

        if rows is not None:
            content["rows"] = rows
        self.send(content)

    def _handle_message(self, _widget: object, content: dict[str, Any], _buffers: object) -> None:
        msg_type = content.get("type")
        if msg_type == SNAPSHOT:
            self._send_snapshot()
        elif msg_type == EDIT:
            self._apply_edit(content)
        elif msg_type == SELECT:
            self.selected = list(content.get("selected") or [])
            for callback in list(self._select_callbacks):
                callback(self)
        elif msg_type == ROW_CLICK:
            row = self._row_map().get(content.get("row_id"))
            if row is not None:
                self._notify_action(dict(row))
                self._notify_click()

    def _apply_edit(self, content: dict[str, Any]) -> None:
        row_id = content.get("row_id")
        field = str(content.get("field"))
        row = self._row_map().get(row_id)
        if row is None:
            # A delete from Python reached the view after the user started editing.
            return

        value = _cell(content.get("value"))
        edit = CellEdit(row_id=row_id, field=field, value=value, old_value=row.get(field))
        row[field] = value
        self._send_delta(DeltaOp.UPDATE, rows=[{self._index: row_id, field: value}], origin=content.get("view"))
        for callback in list(self._edit_callbacks):
            callback(self, edit)


def _cell(value: Any) -> Any:
    # NaN and NaT are the only values unequal to themselves, and JSON has neither.
    if isinstance(value, (float, datetime)) and value != value:
        return None

    return json_value(value)


def _functions(value: Any) -> Any:
    if isinstance(value, JsCode):
        return value

    if isinstance(value, Mapping):
        if len(value) == 1 and isinstance(value.get(FUNCTION_KEY), str):
            return JsCode(value[FUNCTION_KEY])

        return {str(key): _functions(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [_functions(item) for item in value]

    return value


def _wire(value: Any) -> Any:
    if isinstance(value, JsCode):
        return {FUNCTION_KEY: value.source}

    if isinstance(value, Mapping):
        return {str(key): _wire(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [_wire(item) for item in value]

    return _cell(value)


def _arrow() -> Any:
    try:
        import pyarrow
    except ImportError:
        return None

    return pyarrow


def _require_arrow() -> Any:
    arrow = _arrow()
    if arrow is None:
        raise ImportError("transport='arrow' needs pyarrow; install it or use transport='json'")

    return arrow


def _is_pandas(data: Any) -> bool:
    pandas = sys.modules.get("pandas")

    return pandas is not None and isinstance(data, pandas.DataFrame)


def _is_columnar(data: Any) -> bool:
    return _is_pandas(data) or hasattr(data, "__arrow_c_stream__")


def _arrow_table(arrow: Any, data: Any) -> Any:
    # A pandas index is not a column of the rows, as `to_dict("records")` agrees.
    if _is_pandas(data):
        return arrow.Table.from_pandas(data, preserve_index=False)

    if isinstance(data, arrow.Table):
        return data

    return arrow.table(data)


def _wire_table(arrow: Any, table: Any) -> Any:
    """Return ``table`` with every column in a form that matches the JSON rows.

    Dates, times, and timestamps become the ISO 8601 strings Python writes,
    NaN becomes null, and string views become strings.
    """
    compute = arrow.compute
    columns = []
    for field, column in zip(table.schema, table.columns, strict=True):
        kind = field.type
        if arrow.types.is_timestamp(kind) or arrow.types.is_date(kind) or arrow.types.is_time(kind):
            column = arrow.array([_cell(value) for value in column.to_pylist()], arrow.string())
        elif arrow.types.is_floating(kind):
            column = compute.if_else(compute.is_nan(column), arrow.scalar(None, kind), column)
        elif arrow.types.is_string_view(kind) or arrow.types.is_large_string(kind):
            column = column.cast(arrow.string())
        columns.append(column)

    return arrow.table(columns, names=table.column_names)


def _table_rows(table: Any) -> list[dict[str, Any]]:
    return [{name: _cell(value) for name, value in row.items()} for row in table.to_pylist()]


def _check_index_column(arrow: Any, table: Any, index: str) -> None:
    if index not in table.column_names:
        return

    column = table.column(index)
    if column.null_count:
        raise ValueError(f"index field {index!r} is missing from some rows")

    if arrow.compute.count_distinct(column).as_py() != table.num_rows:
        raise ValueError(f"duplicate index values in field {index!r}")


def _ipc(arrow: Any, table: Any) -> memoryview:
    sink = arrow.BufferOutputStream()
    with arrow.ipc.new_stream(sink, table.schema) as writer:
        writer.write_table(table)

    return memoryview(sink.getvalue())


__all__ = ["CellEdit", "JsCode", "Tabulator"]
