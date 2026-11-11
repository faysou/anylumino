import re
from datetime import date
from datetime import datetime
from datetime import time
from pathlib import Path

import anywidget
import pandas as pd
import pytest
import traitlets as t

import anylumino as al
from anylumino import tabulator
from anylumino.tabulator import DELTA
from anylumino.tabulator import EDIT
from anylumino.tabulator import ROW_CLICK
from anylumino.tabulator import SELECT
from anylumino.tabulator import SNAPSHOT


ROWS = [
    {"id": 1, "symbol": "ESZ6", "last": 5012.25},
    {"id": 2, "symbol": "NQZ6", "last": 18011.5},
    {"id": 3, "symbol": "RTYZ6", "last": 2310.1},
]


class Sent:
    """Records the custom messages a widget sends instead of sending them."""

    def __init__(self, widget: al.Tabulator) -> None:
        self.messages: list[tuple[dict, list | None]] = []
        widget.send = lambda content, buffers=None: self.messages.append((content, buffers))

    @property
    def contents(self) -> list[dict]:
        return [content for content, _buffers in self.messages]


def table(rows=ROWS, **kwargs) -> tuple[al.Tabulator, Sent]:
    widget = al.Tabulator([dict(row) for row in rows], **kwargs)

    return widget, Sent(widget)


def frontend(widget: al.Tabulator, content: dict, buffers: list | None = None) -> None:
    widget._handle_message(widget, content, buffers or [])


def test_rows_columns_and_options_sync() -> None:
    widget = al.Tabulator(
        ROWS,
        [{"title": "Symbol", "field": "symbol"}],
        index="id",
        options={"layout": "fitColumns"},
        selected=[2],
        width=600,
        height=0.5,
    )

    assert widget.get_state(["columns", "options", "index", "selected", "width", "height"]) == {
        "columns": [{"title": "Symbol", "field": "symbol"}],
        "options": {"layout": "fitColumns"},
        "index": "id",
        "selected": [2],
        "width": "600px",
        "height": "50%",
    }
    assert widget.data == ROWS
    assert "data" not in widget.get_state()


def test_defaults() -> None:
    widget = al.Tabulator()

    assert widget.get_state(["columns", "options", "index", "selected", "width", "height"]) == {
        "columns": [],
        "options": {},
        "index": "id",
        "selected": [],
        "width": "100%",
        "height": "320px",
    }
    assert widget.data == []
    assert widget.revision == 0


def test_dataframe_rows_match_records() -> None:
    frame = pd.DataFrame({"id": [7, 8, 9], "symbol": ["A", "B", "C"], "qty": [1, -2, 3]})

    widget = al.Tabulator(frame, transport="json")

    assert widget.data == frame.to_dict("records")


def test_rows_without_index_get_sequential_ids() -> None:
    widget = al.Tabulator([{"symbol": "A"}, {"symbol": "B"}, {"symbol": "C"}])

    assert widget.data == [
        {"symbol": "A", "id": 0},
        {"symbol": "B", "id": 1},
        {"symbol": "C", "id": 2},
    ]


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        ([{"id": 1}, {"id": 1}], "duplicate index value 1"),
        ([{"id": 1}, {"symbol": "B"}], "missing from some rows"),
    ],
)
def test_invalid_index_is_rejected(rows, message) -> None:
    with pytest.raises(ValueError, match=message):
        al.Tabulator(rows)


def test_cells_become_json_values() -> None:
    widget = al.Tabulator(
        [{"id": 1, "day": date(2026, 11, 11), "at": time(9, 30), "ts": datetime(2026, 11, 11, 9, 30), "px": float("nan")}],
    )

    assert widget.data == [{"id": 1, "day": "2026-11-11", "at": "09:30:00", "ts": "2026-11-11T09:30:00", "px": None}]


def test_data_returns_copies() -> None:
    widget, _sent = table()

    widget.data[0]["symbol"] = "changed"

    assert widget.data[0]["symbol"] == "ESZ6"


def test_snapshot_request_replies_with_rows_and_revision() -> None:
    widget, sent = table()
    widget.update_rows([{"id": 1, "last": 1.0}])

    frontend(widget, {"type": SNAPSHOT})

    assert sent.messages[-1] == (
        {
            "type": SNAPSHOT,
            "revision": 1,
            "rows": [
                {"id": 1, "symbol": "ESZ6", "last": 1.0},
                {"id": 2, "symbol": "NQZ6", "last": 18011.5},
                {"id": 3, "symbol": "RTYZ6", "last": 2310.1},
            ],
        },
        None,
    )


def test_data_assignment_sends_snapshot_and_drops_missing_selection() -> None:
    widget, sent = table(selected=[1, 3])

    widget.data = [{"id": 3, "symbol": "CLZ6"}, {"id": 4, "symbol": "GCZ6"}]

    assert widget.data == [{"id": 3, "symbol": "CLZ6"}, {"id": 4, "symbol": "GCZ6"}]
    assert widget.revision == 1
    assert sent.contents == [
        {"type": SNAPSHOT, "revision": 1, "rows": [{"id": 3, "symbol": "CLZ6"}, {"id": 4, "symbol": "GCZ6"}]},
    ]
    assert widget.selected == [3]


def test_update_rows_merges_fields_and_sends_changed_rows() -> None:
    widget, sent = table()

    widget.update_rows([{"id": 2, "last": 18012.0}])

    assert widget.data[1] == {"id": 2, "symbol": "NQZ6", "last": 18012.0}
    assert sent.contents == [
        {"type": DELTA, "revision": 1, "op": "update", "origin": None, "rows": [{"id": 2, "last": 18012.0}]},
    ]


@pytest.mark.parametrize("top", [False, True])
def test_add_rows_appends_or_prepends(top) -> None:
    widget, sent = table()

    widget.add_rows([{"id": 9, "symbol": "CLZ6"}], top=top)

    ids = [row["id"] for row in widget.data]
    assert ids == ([9, 1, 2, 3] if top else [1, 2, 3, 9])
    assert sent.contents == [
        {"type": DELTA, "revision": 1, "op": "add", "origin": None, "top": top, "rows": [{"id": 9, "symbol": "CLZ6"}]},
    ]


def test_add_rows_continues_assigned_ids() -> None:
    widget = al.Tabulator([{"symbol": "A"}, {"symbol": "B"}])

    widget.add_rows([{"symbol": "C"}])

    assert [row["id"] for row in widget.data] == [0, 1, 2]


def test_upsert_rows_updates_existing_and_appends_new() -> None:
    widget, sent = table()

    widget.upsert_rows([{"id": 1, "last": 1.5}, {"id": 4, "symbol": "GCZ6"}])

    assert widget.data == [
        {"id": 1, "symbol": "ESZ6", "last": 1.5},
        {"id": 2, "symbol": "NQZ6", "last": 18011.5},
        {"id": 3, "symbol": "RTYZ6", "last": 2310.1},
        {"id": 4, "symbol": "GCZ6"},
    ]
    assert sent.contents == [
        {
            "type": DELTA,
            "revision": 1,
            "op": "upsert",
            "origin": None,
            "rows": [{"id": 1, "last": 1.5}, {"id": 4, "symbol": "GCZ6"}],
        },
    ]


def test_delete_rows_removes_rows_and_selection() -> None:
    widget, sent = table(selected=[1, 2])

    widget.delete_rows([2, 3])

    assert widget.data == [{"id": 1, "symbol": "ESZ6", "last": 5012.25}]
    assert widget.selected == [1]
    assert sent.contents == [{"type": DELTA, "revision": 1, "op": "delete", "origin": None, "ids": [2, 3]}]


@pytest.mark.parametrize(
    ("change", "error"),
    [
        (lambda widget: widget.update_rows([{"id": 1, "last": 0.0}, {"id": 99, "last": 0.0}]), KeyError),
        (lambda widget: widget.update_rows([{"last": 0.0}]), ValueError),
        (lambda widget: widget.add_rows([{"id": 4}, {"id": 2}]), ValueError),
        (lambda widget: widget.add_rows([{"symbol": "no id"}]), ValueError),
        (lambda widget: widget.upsert_rows([{"symbol": "no id"}]), ValueError),
        (lambda widget: widget.delete_rows([1, 99]), KeyError),
    ],
)
def test_invalid_changes_leave_rows_unchanged(change, error) -> None:
    widget, sent = table()

    with pytest.raises(error):
        change(widget)

    assert widget.data == ROWS
    assert widget.revision == 0
    assert sent.messages == []


@pytest.mark.parametrize(
    "change",
    [
        lambda widget: widget.update_rows([]),
        lambda widget: widget.add_rows([]),
        lambda widget: widget.upsert_rows([]),
        lambda widget: widget.delete_rows([]),
    ],
)
def test_empty_changes_send_nothing(change) -> None:
    widget, sent = table()

    change(widget)

    assert widget.revision == 0
    assert sent.messages == []


def test_index_change_rekeys_rows_and_clears_selection() -> None:
    widget, _sent = table(selected=[1])

    widget.index = "symbol"
    widget.update_rows([{"symbol": "NQZ6", "last": 1.0}])

    assert widget.data[1] == {"id": 2, "symbol": "NQZ6", "last": 1.0}
    assert widget.selected == []


def test_index_change_to_missing_field_is_rejected() -> None:
    widget, _sent = table()

    with pytest.raises(t.TraitError, match="every row needs this field"):
        widget.index = "venue"

    assert widget.index == "id"


def test_options_reject_arguments_of_their_own() -> None:
    with pytest.raises(t.TraitError, match="options cannot set data, index"):
        al.Tabulator(ROWS, options={"data": [], "index": "symbol"})


def test_selected_drops_unknown_ids() -> None:
    widget, _sent = table()

    widget.selected = [1, 3, 99]

    assert widget.selected == [1, 3]


def test_frontend_selection_sets_selected_and_runs_callbacks() -> None:
    widget, _sent = table()
    calls = []
    removed = []

    def unregistered(item):
        removed.append(item)

    widget.on_select(lambda item: calls.append(list(item.selected)))
    widget.on_select(unregistered)
    widget.on_select(unregistered, remove=True)

    frontend(widget, {"type": SELECT, "selected": [3, 1]})

    assert widget.selected == [3, 1]
    assert calls == [[3, 1]]
    assert removed == []


def test_frontend_edit_patches_row_runs_callbacks_and_rebroadcasts() -> None:
    widget, sent = table()
    edits = []
    widget.on_edit(lambda item, edit: edits.append((item, edit)))

    frontend(widget, {"type": EDIT, "view": "view-a", "row_id": 2, "field": "last", "value": 18100.0, "old_value": 18011.5})

    assert widget.data[1] == {"id": 2, "symbol": "NQZ6", "last": 18100.0}
    assert edits == [(widget, al.CellEdit(row_id=2, field="last", value=18100.0, old_value=18011.5))]
    assert sent.contents == [
        {"type": DELTA, "revision": 1, "op": "update", "origin": "view-a", "rows": [{"id": 2, "last": 18100.0}]},
    ]


def test_frontend_edit_of_deleted_row_is_ignored() -> None:
    widget, sent = table()
    edits = []
    widget.on_edit(lambda item, edit: edits.append(edit))

    frontend(widget, {"type": EDIT, "view": "view-a", "row_id": 99, "field": "last", "value": 1.0, "old_value": 0.0})

    assert widget.data == ROWS
    assert edits == []
    assert sent.messages == []


def test_frontend_row_click_runs_click_and_action_callbacks() -> None:
    widget, _sent = table()
    clicks = []
    actions = []
    widget.on_click(clicks.append)
    widget.on_action(lambda item, row: actions.append(row))

    frontend(widget, {"type": ROW_CLICK, "row_id": 2})

    assert clicks == [widget]
    assert actions == [{"id": 2, "symbol": "NQZ6", "last": 18011.5}]


def test_constructor_callbacks_register_row_click_callbacks() -> None:
    clicks = []
    actions = []
    widget = al.Tabulator(ROWS, callbacks=[clicks.append], action_callbacks=[lambda item, row: actions.append(row["id"])])

    frontend(widget, {"type": ROW_CLICK, "row_id": 3})

    assert clicks == [widget]
    assert actions == [3]


STATIC = Path(__file__).resolve().parents[1] / "src" / "anylumino" / "static" / "tabulator"


def frontend_source() -> str:
    return "\n".join(path.read_text() for path in sorted([*STATIC.glob("*.mjs"), STATIC / "tabulator_widget.js"]))


def frontend_constants(source: str) -> dict[str, str]:
    return dict(re.findall(r'^\s*(?:export const )?([A-Z_]+):? (?:= )?"([^"]+)"', source, re.M))


def test_message_types_and_wire_names_match_the_frontend() -> None:
    constants = frontend_constants(frontend_source())

    assert {name: constants[name] for name in ("SNAPSHOT", "DELTA", "EDIT", "SELECT", "ROW_CLICK", "FUNCTION_KEY")} == {
        "SNAPSHOT": tabulator.SNAPSHOT,
        "DELTA": tabulator.DELTA,
        "EDIT": tabulator.EDIT,
        "SELECT": tabulator.SELECT,
        "ROW_CLICK": tabulator.ROW_CLICK,
        "FUNCTION_KEY": tabulator.FUNCTION_KEY,
    }
    assert {constants[op.name] for op in tabulator.DeltaOp} == {op.value for op in tabulator.DeltaOp}


def test_synced_traits_match_the_frontend() -> None:
    source = frontend_source()
    read = set(re.findall(r'model\.get\("([a-z_]+)"\)', source)) | set(re.findall(r'^\s*\["([a-z_]+)", ', source, re.M))
    # anywidget's own traits, such as `_esm` and `_css`, are private.
    synced = {name for name in al.Tabulator().traits(sync=True) if not name.startswith("_")} - set(
        anywidget.AnyWidget().traits(sync=True)
    )

    assert read == synced == {"columns", "options", "index", "selected", "width", "height"}


FRAME = pd.DataFrame(
    {
        "symbol": ["ESZ6", "NQZ6"],
        "last": [5012.25, float("nan")],
        "qty": [3, -1],
        "live": [True, False],
        "ts": [datetime(2026, 11, 11, 9, 30), None],
        "note": [None, "halt"],
    }
)
FRAME_ROWS = [
    {"symbol": "ESZ6", "last": 5012.25, "qty": 3, "live": True, "ts": "2026-11-11T09:30:00", "note": None, "id": 0},
    {"symbol": "NQZ6", "last": None, "qty": -1, "live": False, "ts": None, "note": "halt", "id": 1},
]


def ipc_rows(buffer) -> list[dict]:
    import pyarrow as pa

    return pa.ipc.open_stream(bytes(buffer)).read_all().to_pylist()


@pytest.mark.parametrize(
    ("data", "transport", "arrow"),
    [
        (FRAME, "auto", True),
        (FRAME, "json", False),
        (FRAME_ROWS, "auto", False),
        (FRAME_ROWS, "arrow", True),
    ],
)
def test_transport_selection(data, transport, arrow) -> None:
    widget = al.Tabulator(data, transport=transport)
    sent = Sent(widget)

    frontend(widget, {"type": SNAPSHOT})

    content, buffers = sent.messages[-1]
    if arrow:
        assert content == {"type": SNAPSHOT, "revision": 0, "format": "arrow"}
        assert ipc_rows(buffers[0]) == FRAME_ROWS
    else:
        assert (content, buffers) == ({"type": SNAPSHOT, "revision": 0, "rows": FRAME_ROWS}, None)


def test_arrow_and_json_give_equal_rows() -> None:
    assert al.Tabulator(FRAME).data == al.Tabulator(FRAME, transport="json").data == FRAME_ROWS


def test_arrow_snapshot_reuses_the_source_until_a_change() -> None:
    widget = al.Tabulator(FRAME)
    sent = Sent(widget)

    frontend(widget, {"type": SNAPSHOT})
    first_rows_built = widget._rows is not None
    widget.update_rows([{"id": 1, "last": 18011.5}])
    frontend(widget, {"type": SNAPSHOT})

    assert first_rows_built is False
    assert ipc_rows(sent.messages[-1][1][0])[1]["last"] == 18011.5


def test_add_rows_sends_columnar_batches_as_arrow() -> None:
    widget = al.Tabulator(FRAME)
    sent = Sent(widget)

    widget.add_rows(pd.DataFrame({"symbol": ["CLZ6"], "qty": [2]}))

    content, buffers = sent.messages[-1]
    assert content == {"type": DELTA, "revision": 1, "op": "add", "origin": None, "top": False, "format": "arrow"}
    assert ipc_rows(buffers[0]) == [{"symbol": "CLZ6", "qty": 2, "id": 2}]
    assert widget.data[-1] == {"symbol": "CLZ6", "qty": 2, "id": 2}


@pytest.mark.parametrize(
    ("frame", "message"),
    [
        (pd.DataFrame({"id": [1, 1]}), "duplicate index values"),
        (pd.DataFrame({"id": [1.0, None]}), "missing from some rows"),
    ],
)
def test_arrow_input_with_invalid_index_is_rejected(frame, message) -> None:
    with pytest.raises(ValueError, match=message):
        al.Tabulator(frame)


def test_without_pyarrow(monkeypatch) -> None:
    monkeypatch.setattr(tabulator, "_arrow", lambda: None)
    widget = al.Tabulator(FRAME)
    sent = Sent(widget)

    frontend(widget, {"type": SNAPSHOT})

    assert sent.messages[-1] == ({"type": SNAPSHOT, "revision": 0, "rows": FRAME_ROWS}, None)
    with pytest.raises(ImportError, match="needs pyarrow"):
        al.Tabulator(FRAME, transport="arrow")


def test_transport_rejects_unknown_values() -> None:
    with pytest.raises(ValueError, match="transport='csv' is not a valid Transport"):
        al.Tabulator(transport="csv")


def test_js_code_serializes_at_any_depth() -> None:
    widget = al.Tabulator(
        columns=[
            {
                "field": "px",
                "formatter": al.JsCode("function(cell) { return 1; }"),
                "headerMenu": [{"label": "Hide", "action": {"$js": "(event, column) => column.hide()"}}],
            }
        ],
        options={"rowFormatter": al.JsCode("function(row) {}"), "columnDefaults": {"sorter": {"$js": "(a, b) => a - b"}}},
    )

    assert widget.columns[0]["headerMenu"][0]["action"] == al.JsCode("(event, column) => column.hide()")
    assert widget.get_state(["columns", "options"]) == {
        "columns": [
            {
                "field": "px",
                "formatter": {"$js": "function(cell) { return 1; }"},
                "headerMenu": [{"label": "Hide", "action": {"$js": "(event, column) => column.hide()"}}],
            }
        ],
        "options": {"rowFormatter": {"$js": "function(row) {}"}, "columnDefaults": {"sorter": {"$js": "(a, b) => a - b"}}},
    }


@pytest.mark.parametrize("value", [{"$js": "f", "note": 1}, {"$js": 42}])
def test_mappings_that_are_not_the_wire_form_stay_mappings(value) -> None:
    widget = al.Tabulator(options={"meta": value})

    assert widget.options == {"meta": value}
    assert widget.get_state("options") == {"options": {"meta": value}}


def test_columns_must_be_mappings() -> None:
    with pytest.raises(t.TraitError, match="one mapping per column"):
        al.Tabulator(columns=["symbol"])


def test_delta_dates_become_iso_strings() -> None:
    widget, sent = table([{"id": 1, "ts": datetime(2026, 11, 11, 9, 30)}])

    widget.update_rows([{"id": 1, "ts": datetime(2026, 11, 12, 10, 0)}])
    widget.add_rows([{"id": 2, "ts": date(2026, 11, 13)}])

    assert [content["rows"] for content in sent.contents] == [
        [{"id": 1, "ts": "2026-11-12T10:00:00"}],
        [{"id": 2, "ts": "2026-11-13"}],
    ]
