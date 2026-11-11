## Why

anylumino has no table for large or live data. `ax.Table` renders every row through React with no
virtualization, editing, filtering, or grouping, and `itables.ITable` is a third-party widget that
resends the whole DataFrame on each update. A trading blotter needs a virtualized grid that takes
row deltas at tick rate, so this change wraps [Tabulator](https://tabulator.info) 6.7.1 (MIT) as
a first-party anylumino widget.

## What Changes

- Add `al.Tabulator`, a virtualized data grid built on `tabulator-tables` 6.7.1 from npm, bundled
  and loaded through the existing `SharedBundleWidget` loader.
- Keep the rows in Python and send them over a message channel: a snapshot on render, then row
  deltas from `update_rows`, `add_rows`, `upsert_rows`, and `delete_rows`.
- Send snapshots and added batches as Arrow IPC when the input is columnar and `pyarrow` imports,
  and as JSON otherwise. A `transport` option forces either.
- Report selection, cell edits, and row clicks to Python through `selected`, `on_select`,
  `on_edit`, `on_click`, and `on_action`.
- Add `al.JsCode`, which marks a JavaScript function source so the browser passes a real function
  to Tabulator for formatters, sorters, editors, validators, mutators, and menus.
- Bundle `luxon` so Tabulator's `datetime` formatter, sorter, and editors work by name, and send
  Python `date`, `time`, and `datetime` cells as ISO 8601 strings.
- Add a `Tabulator` component to the workbench catalog, including JavaScript function values in
  its columns and options.
- Add notebooks, documentation, a changelog entry, and the regenerated license inventory.

## Capabilities

### New Capabilities

- `tabulator-table`: the `al.Tabulator` widget and `al.JsCode`: construction, the row data
  channel and its transports, row deltas, events, JavaScript function values, dates, theming, and
  hosting inside layout panels and shadow roots.

### Modified Capabilities

- `openui-codegen`: the component catalog gains a `Tabulator` component whose columns and options
  may carry JavaScript function values.

## Impact

- **Python:** new `src/anylumino/tabulator.py`; exports in `src/anylumino/__init__.py`; one
  catalog entry in `src/anylumino/workbench/catalog.py`; a regenerated skill page under
  `src/anylumino/workbench/plugin/skills/openui-components/components/`.
- **Frontend:** new `src/anylumino/static/tabulator/`; one entry in `scripts/bundle-entries.mjs`.
- **Dependencies:** npm `tabulator-tables` 6.7.1 (MIT), `luxon` 3.7.2 (MIT), and
  `@uwdata/flechette` 2.8.0 (BSD-3-Clause), all bundled. `pyarrow` is an optional runtime import
  and a new dev dependency; `pandas` stays a dev dependency.
- **Package size:** the wheel grows by one bundle. The bundle loads only on pages that show a
  `Tabulator`.
- **Security:** `al.JsCode` runs its source in the notebook page. The workbench catalog accepts
  it, so an agent-written program can run JavaScript in the page that displays the workbench.
- **Existing widgets:** no change to `ax.Table`, the layout panels, or their bundles.
