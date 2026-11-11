# tabulator-table Specification

## Purpose
The `Tabulator` widget and `JsCode`: a virtualized data grid whose rows Python holds and changes
by delta, with selection, cell edits, row clicks, and JavaScript function options.

## Requirements

### Requirement: Tabulator widget construction

The system SHALL provide `al.Tabulator`, a virtualized data grid built on Tabulator 6.7.1.
`columns` SHALL hold Tabulator column definitions and `options` SHALL hold any other Tabulator
constructor option, both passed to Tabulator under Tabulator's own names. Without `columns` the
grid SHALL derive its columns from the data. `data` SHALL accept a list of row mappings, an object
with `to_dict("records")`, or an object with `__arrow_c_stream__`.

#### Scenario: Rows and columns render

- **WHEN** `al.Tabulator([{"id": 1, "symbol": "ESZ6"}], [{"title": "Symbol", "field": "symbol"}])`
  is displayed
- **THEN** the grid shows one row with `ESZ6` under a `Symbol` header

#### Scenario: Columns derived from data

- **WHEN** a `Tabulator` is created with rows and no `columns`
- **THEN** the grid shows one column per row field

#### Scenario: DataFrame input

- **WHEN** a pandas DataFrame with three rows is passed as `data`
- **THEN** `table.data` returns three row mappings with the DataFrame's column names as keys

### Requirement: Row identity

Every row SHALL carry a unique value under the `index` field, `"id"` by default. When no row of the
initial data has that field, the widget SHALL assign sequential ids under it. Data with a duplicate
or partly missing index SHALL raise `ValueError` and leave the rows unchanged.

#### Scenario: Ids assigned

- **WHEN** rows without an `id` field are passed with the default `index`
- **THEN** `table.data` rows carry `id` values `0, 1, 2, ...` in input order

#### Scenario: Duplicate index rejected

- **WHEN** `add_rows` receives a row whose index value an existing row has
- **THEN** it raises `ValueError` and `table.data` is unchanged

### Requirement: Row data channel

Python SHALL hold the rows and a revision counter. A view SHALL request a snapshot when it renders
and SHALL show the rows and take the revision of the reply. Assigning `table.data` SHALL replace
the rows in every view and keep each view's sort and scroll position.

#### Scenario: Second view shows current rows

- **WHEN** a widget whose rows were changed by deltas is displayed in a second cell
- **THEN** the second view shows the same rows as the first

#### Scenario: Data assignment keeps sort

- **WHEN** a view is sorted by a column and `table.data` is assigned new rows
- **THEN** the view shows the new rows in that sort order

### Requirement: Row deltas

`update_rows`, `add_rows`, `upsert_rows`, and `delete_rows` SHALL change the Python rows, add one
to the revision, and send one delta message that carries only the changed rows. `update_rows` SHALL
raise `KeyError` for an unknown index value. `add_rows` SHALL append, or prepend with `top=True`.
`upsert_rows` SHALL update rows whose index exists and add the others. A view SHALL apply the
deltas of one animation frame in a single repaint.

#### Scenario: Update changes one cell

- **WHEN** `table.update_rows([{"id": 1, "last": 5012.25}])` runs on a displayed table
- **THEN** the view shows `5012.25` in that row, the other cells of the row are unchanged, and the
  message carries one row

#### Scenario: Unknown row

- **WHEN** `update_rows` receives an index value no row has
- **THEN** it raises `KeyError`, the revision is unchanged, and no message is sent

#### Scenario: Upsert mixes update and add

- **WHEN** `upsert_rows` receives one existing and one new index value
- **THEN** `table.data` has the existing row updated and the new row appended

#### Scenario: Delete

- **WHEN** `table.delete_rows([1])` runs
- **THEN** the row is gone from `table.data` and from every view, and from `selected` if it was
  selected

### Requirement: Views recover from a missed delta

A view SHALL apply a delta only when the delta's revision is the view's revision plus one. For any
other revision it SHALL discard the delta and request a snapshot.

#### Scenario: Revision gap

- **WHEN** a view at revision 4 receives a delta with revision 6
- **THEN** it requests a snapshot and then shows the rows of the reply

#### Scenario: Delta before the first snapshot

- **WHEN** a delta arrives before the view's snapshot reply
- **THEN** the view discards it and shows the snapshot's rows

### Requirement: Arrow and JSON transports

Snapshots and `add_rows` batches SHALL travel as an Arrow IPC stream in binary buffers when the
input is columnar and `pyarrow` is importable, and as JSON otherwise. `transport` SHALL take a
`Transport` enum that forces JSON or Arrow; forcing Arrow without `pyarrow` SHALL raise
`ImportError`. Both transports SHALL produce equal rows in the view.

#### Scenario: Automatic Arrow

- **WHEN** a DataFrame is passed and `pyarrow` is installed
- **THEN** the snapshot reply carries the rows in a binary buffer

#### Scenario: Fallback to JSON

- **WHEN** a list of row mappings is passed
- **THEN** the snapshot reply carries the rows as JSON

#### Scenario: Equal rows

- **WHEN** the same DataFrame with string, integer, float, boolean, null, and datetime columns is
  shown once with each transport
- **THEN** both views hold the same row objects

### Requirement: Selection

`selected` SHALL hold the index values of the selected rows and SHALL sync both ways. A selection
made in the view SHALL run the `on_select` callbacks. An assigned index value that no row has SHALL
be dropped.

#### Scenario: User selects a row

- **WHEN** the user selects the row with index `7` in a table with row selection enabled
- **THEN** `table.selected` is `[7]` and each `on_select` callback runs once with the widget

#### Scenario: Python selects rows

- **WHEN** `table.selected = [1, 3, 99]` is assigned and no row has index `99`
- **THEN** the view selects rows `1` and `3` and `table.selected` is `[1, 3]`

### Requirement: Cell edits

A cell edit in the view SHALL update the Python row, add one to the revision, run the `on_edit`
callbacks with the row id, field, new value, and old value, and reach every other view of the
widget. The editing view SHALL NOT reapply its own edit.

#### Scenario: Edit reaches Python

- **WHEN** the user changes `qty` from `10` to `12` in the row with index `3`
- **THEN** `table.data` has `qty == 12` for that row and `on_edit` receives
  `Edit(row_id=3, field="qty", value=12, old_value=10)`

#### Scenario: Edit reaches a second view

- **WHEN** the widget is displayed twice and a cell is edited in one view
- **THEN** the other view shows the new value

### Requirement: Row activation

A row click SHALL run the `on_click` callbacks and SHALL run the `on_action` callbacks with the row
mapping.

#### Scenario: Row clicked

- **WHEN** the user clicks the row with index `2`
- **THEN** `on_action` receives the widget and the mapping of row `2`

### Requirement: JavaScript function values

`al.JsCode(source)` SHALL mark JavaScript function source. Wherever a `JsCode` appears inside
`columns` or `options`, Tabulator SHALL receive the function the source evaluates to. A mapping
with the single key `$js` and a string value SHALL be equivalent to `JsCode`. A source that does
not evaluate to a function SHALL show an error that names the option path, and the grid SHALL NOT
render.

#### Scenario: Custom formatter

- **WHEN** a column sets `"formatter": al.JsCode("function(cell) { return cell.getValue() + '!'; }")`
- **THEN** a cell with value `a` shows `a!`

#### Scenario: Wire form as input

- **WHEN** a column sets `"formatter": {"$js": "function(cell) { return 'x'; }"}`
- **THEN** every cell of that column shows `x`

#### Scenario: Invalid source

- **WHEN** a column formatter is `al.JsCode("not a function (")`
- **THEN** the widget shows an error naming `columns[0].formatter` and no grid

### Requirement: Date and time cells

Python `date`, `time`, and `datetime` cell values SHALL reach the view as ISO 8601 strings.
Tabulator's `datetime` formatter, sorter, and editors SHALL work by name without the page providing
luxon.

#### Scenario: Datetime formatter by name

- **WHEN** a column sets `"formatter": "datetime"` with
  `"formatterParams": {"inputFormat": "iso", "outputFormat": "dd/MM/yyyy"}` and a cell holds
  `datetime(2026, 11, 11, 9, 30)`
- **THEN** the cell shows `11/11/2026`

### Requirement: Hosting in layouts and shadow roots

A `Tabulator` SHALL lay out correctly as a child of every anylumino layout panel, including when
its tab is first shown after being hidden and when its panel is resized. In a shadow root, its
popups SHALL render inside the widget root so the widget styles apply. Removing the view SHALL
destroy the Tabulator instance.

#### Scenario: Hidden tab revealed

- **WHEN** a `Tabulator` in the second tab of a `TabPanel` is shown for the first time
- **THEN** its header and rows fill the tab's width and the rows are visible

#### Scenario: Popup in a shadow root

- **WHEN** a header menu opens on a `Tabulator` rendered inside a shadow root
- **THEN** the menu element is a descendant of the widget root

### Requirement: Theme follows the host

The grid SHALL use the host's light or dark colors in JupyterLab and SHALL fall back to a light
theme where the host defines no theme variables.

#### Scenario: JupyterLab dark theme

- **WHEN** a `Tabulator` is displayed under the JupyterLab dark theme
- **THEN** its row background is dark and its text is light
