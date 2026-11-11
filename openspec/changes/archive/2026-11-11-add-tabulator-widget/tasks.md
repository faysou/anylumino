# Tasks

## 1. Widget and row data channel

- [x] 1.1 Add `tabulator-tables` pinned to `6.7.1` to `package.json`, add
  `static/tabulator/tabulator_widget.js` that renders a `TabulatorFull` from `columns` and
  `options`, and add its entry to `scripts/bundle-entries.mjs`; verify `npm run build` writes
  `tabulator_widget.bundle.js` and `tabulator_widget.loader.js`.
- [x] 1.2 Add `src/anylumino/tabulator.py` with `Tabulator` on `ActivationCallbacks` and
  `SharedBundleWidget` per design D2 (traits `columns`, `options`, `index`, `selected`, `width`,
  `height`; `data` property) and export it from `anylumino/__init__.py`; verify tests in
  `tests/test_tabulator_widget.py` for list, `to_dict("records")`, and missing-columns input.
- [x] 1.3 Implement row identity per the spec (dict keyed by `index`, assigned ids, `ValueError` on
  duplicate or partly missing index); verify parametrized tests for each case.
- [x] 1.4 Implement the snapshot request and reply and the revision counter on both sides, and
  `table.data` assignment through `replaceData`; verify a Python test of the reply payload and a
  frontend test of snapshot handling in `tests/frontend/tabulator_widget.test.mjs`.
- [x] 1.5 Implement `update_rows`, `add_rows`, `upsert_rows`, and `delete_rows` with one delta
  message each; verify Python tests of rows, revision, message content, and the `KeyError` and
  `ValueError` paths leaving state unchanged.
- [x] 1.6 Apply deltas in the view inside `blockRedraw` and `restoreRedraw`, coalesced per frame,
  with the revision-gap and pre-snapshot rules as pure functions; verify frontend tests for in-order
  deltas, a gap, and a delta before the snapshot.
- [x] 1.7 Add a contract test that the trait names and message types in `tabulator.py` match the
  frontend source, following `tests/test_contract.py`; verify it fails when one side is renamed.

## 2. Events, hosting, and theme

- [x] 2.1 Sync `selected` both ways and add `on_select`; verify Python tests for assignment,
  dropped unknown ids, and callback registration and removal.
- [x] 2.2 Handle `cellEdited`: patch the Python row, bump the revision, run `on_edit` with an
  `Edit` dataclass, and rebroadcast with the origin view id; verify Python tests for the patched
  row, the callback argument, and the rebroadcast message.
- [x] 2.3 Route `rowClick` to `on_click` and `on_action`; verify a Python test with a simulated
  frontend message.
- [x] 2.4 Set `popupContainer` to the widget root in a shadow root and call `table.destroy()` on
  the render signal; verify a frontend test of the container choice.
- [x] 2.5 Add `tests/browser/test_tabulator.py` covering render, header sort, row selection, a cell
  edit reaching Python and a second view, a rerun cell, a hidden `TabPanel` tab revealed, and a
  `SplitPanel` resize; verify `make test-browser` passes.
- [x] 2.6 Run a marimo notebook with a header menu, a list editor, and a column resize; verify the
  popups are styled and fix or document any shadow-root defect.
- [x] 2.7 Add `static/tabulator/tabulator_widget.css` with `tabulator_simple.css` and the
  JupyterLab variable overrides per design D8; verify a browser test that reads the row background
  under the JupyterLab light and dark themes.

## 3. Arrow transport

- [x] 3.1 Add the `Transport` enum to `anylumino/enums.py` and the `transport` option; encode
  snapshots and `add_rows` batches as an Arrow IPC stream in message buffers when the input is
  columnar and `pyarrow` imports, with the lazy row dict of design D4; add `pyarrow` to the dev
  group; verify Python tests for automatic selection, forced JSON, and `ImportError` on forced Arrow
  without `pyarrow`.
- [x] 3.2 Add `@uwdata/flechette` pinned to `2.8.0` and decode buffers to row objects in the view,
  with timestamp and date columns as ISO strings; verify a frontend test that decodes a fixture
  stream written by `pyarrow`.
- [x] 3.3 Verify with a browser test that one DataFrame with string, integer, float, boolean, null,
  and datetime columns gives equal row objects under both transports.
- [x] 3.4 Measure kernel encode time, message size, and browser time to first paint for 100,000
  rows by 20 columns under both transports, and the bundle size with and without flechette; record
  the numbers in `design.md` and drop tasks 3.1 to 3.3 from the release if Arrow is not faster end
  to end.

## 4. JavaScript function values

- [x] 4.1 Add `al.JsCode` with the `{"$js": source}` wire form and accept that mapping as input,
  serializing through `columns` and `options` at any depth; verify Python tests for nesting, the
  mapping form, and a mapping with extra keys staying a plain mapping.
- [x] 4.2 Revive `$js` objects into functions in the view and show a load error naming the option
  path for a source that does not evaluate to a function; verify frontend tests for a formatter, a
  nested menu action, and both failure cases.
- [x] 4.3 Verify with a browser test a `JsCode` formatter, a `JsCode` sorter, and a header menu
  whose action is a `JsCode`.

## 5. Dates

- [x] 5.1 Add `luxon` pinned to `3.7.2` and pass `dependencies: {DateTime}` to the Tabulator
  constructor; convert `date`, `time`, and `datetime` cells with `json_value` on snapshots and
  deltas; verify a Python test of the serialized cells and a browser test of the `datetime`
  formatter and sorter by name.

## 6. Workbench

- [x] 6.1 Add the `Tabulator` component to `workbench/catalog.py` with `data`, `columns`, and the
  generated options; verify the catalog tests and a codegen test that a program with a `$js`
  formatter generates Python holding the same mapping.
- [x] 6.2 Run `make workbench-skill` and document the `$js` form and that its source runs in the
  page on the component's skill page; verify `tests/test_workbench_skills.py` passes.
- [x] 6.3 Extend the fake-agent workbench browser test with a program that places a `Tabulator` and
  a callback that calls `update_rows`; verify the grid shows the updated cell.

## 7. Documentation and release files

- [x] 7.1 Add `notebooks/tabulator_table.py` (columns, selection, editing, `JsCode`, dates) and
  `notebooks/tabulator_streaming.py` (batched `upsert_rows` at 10 Hz inside a `TabPanel`); format
  both with `make format-notebook-layout` from `option_trader`; verify both run headless with exit
  code 0 and `tests/test_examples.py` passes.
- [x] 7.2 Add a README section and a `content/docs` example with a screenshot, state the workbench
  JavaScript behavior in `content/docs/workbench.mdx`, and run `make docs-reference`; verify
  `make docs-check` passes.
- [x] 7.3 Add the `CHANGELOG.md` entry and run `npm run licenses`; verify
  `THIRD_PARTY_LICENSES.md` lists `tabulator-tables`, `luxon`, and `@uwdata/flechette` and the
  release license check passes.
- [x] 7.4 Run `make test` and `make test-browser`; verify both pass.
