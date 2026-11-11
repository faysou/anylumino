# Spec Delta

## Purpose

Python wrappers for Astryx components: how options, table rows, values, attributes, and child
widgets move between the kernel and the browser, and what stays true as they change.

## ADDED Requirements

### Requirement: Option values are strings

Every option a widget sends to the browser SHALL carry a string value, whether the option was
given as a bare scalar, a `(label, value)` pair, a mapping entry, or a record. A widget's `value`
SHALL hold that string, at construction and after any user interaction.

#### Scenario: Numeric scalar options render

- **WHEN** `Selector([1, 5, 10], value=5)` is displayed
- **THEN** it renders three options, `5` is selected, and `value` is `"5"`

#### Scenario: Slider value keeps one type

- **WHEN** `SelectionSlider([1, 2, 3])` is created and the user then drags it to the second
  option
- **THEN** `value` is `"1"` before the drag and `"2"` after it

#### Scenario: Pair and mapping options are unchanged

- **WHEN** a widget is created with options `{"Low": 1}` or `[("Low", 1)]`
- **THEN** its option value is `"1"`, as before this change

### Requirement: Appending table rows

`append_row` and `prepend_row` SHALL add a row to any table. When row ids are generated, the new
row SHALL receive an id that no existing row uses.

#### Scenario: Append to a table of mappings without ids

- **WHEN** `Table([{"a": 1}, {"a": 2}]).append_row({"a": 3})` is called
- **THEN** the table has three rows with three distinct ids, in that order

#### Scenario: Prepend to a table of sequences

- **WHEN** `Table([[1, 2], [3, 4]]).prepend_row([5, 6])` is called
- **THEN** the new row is first and its id differs from the other two

#### Scenario: Explicit duplicate id is still rejected

- **WHEN** a row whose own id matches an existing row is appended
- **THEN** a `ValueError` names the duplicate id

### Requirement: Table rows keep their data

A table SHALL keep all data of the rows it was given, so that row flags the browser reads
(`selectable`, `enabled`) work without being columns, and changing `columns` shows values the
rows already had.

#### Scenario: Row flag without a column

- **WHEN** a table is created from `[{"id": "x", "a": 1, "selectable": False}]` with
  `columns=["a"]`
- **THEN** row `x` cannot be selected in the browser

#### Scenario: Columns widened after construction

- **WHEN** a table is created from `[{"a": 1, "b": 2}]` with `columns=["a"]` and `columns` is
  then set to `["a", "b"]`
- **THEN** the row shows `2` in column `b`

### Requirement: Search inputs keep picked items

A `Typeahead` or `Tokenizer` with a Python `search` SHALL show every picked item, including items
that came from search results or were created by the user, and a `Tokenizer` SHALL add each pick
to the earlier ones.

#### Scenario: Typeahead shows a searched pick

- **WHEN** the user picks a search result that is not in the widget's static items
- **THEN** the input shows that item as selected and `value` is its id

#### Scenario: Tokenizer accumulates picks

- **WHEN** the user picks two search results one after the other
- **THEN** the input shows two tokens and `value` lists both ids in pick order

#### Scenario: A model change during a search keeps the results

- **WHEN** a Python search is in flight and another trait of the widget changes
- **THEN** the search results still arrive and are shown

### Requirement: Child state survives hiding

A child widget SHALL keep its browser state when its slot is hidden and shown again, and its view
SHALL be released when its slot is removed. Hiding and showing a parent SHALL NOT increase the
number of live child views.

#### Scenario: Split panel inside an unselected tab

- **WHEN** an Astryx `TabPanel` holds a `SplitPanel` whose child has browser state, and the user
  switches away from that tab and back
- **THEN** the child shows the same state and was rendered once

#### Scenario: Inline dialog reopened

- **WHEN** an inline `Dialog` with a child is closed and opened ten times
- **THEN** exactly one view of the child is live afterwards

### Requirement: File input shows the selection

`FileInput` SHALL show the name of the chosen file, or the number of chosen files, after the user
picks.

#### Scenario: Single file picked

- **WHEN** the user picks `report.csv`
- **THEN** the control shows `report.csv` and `value` holds its metadata

### Requirement: Accordion open keys track children

An Astryx `AccordionPanel` SHALL list only existing children in its open keys, and SHALL NOT run
activation callbacks while it is being constructed.

#### Scenario: Open child removed

- **WHEN** child `a` is open and is removed
- **THEN** the open keys no longer contain `a`

#### Scenario: Callbacks passed to the constructor

- **WHEN** an accordion is created with `callbacks=[f]`
- **THEN** `f` has not been called when the constructor returns

### Requirement: Attributes have one source

Each widget attribute SHALL reach the browser from one place. Assigning `label`, `variant`,
`disabled`, or `icon` after display SHALL update the rendered widget, and every constructor
argument that a wrapper accepts SHALL affect what is rendered.

#### Scenario: Label updated after display

- **WHEN** a displayed `DropdownMenu` has its `label` assigned
- **THEN** its button shows the new label

#### Scenario: Disabled container arguments apply

- **WHEN** `Pagination(disabled=True)`, `ContextMenu(disabled=True)`, or
  `ButtonGroup(disabled=True)` is displayed
- **THEN** the rendered control is disabled

### Requirement: Kernel and browser agree on the widget contract

The package SHALL fail its test suite when a synced trait is not read by the browser code, when a
Python component name has no browser entry, or when a message type sent by one side has no handler
on the other. An unknown component name SHALL render a visible error.

#### Scenario: Unread trait

- **WHEN** a synced trait is added to a widget class and the browser code does not read it
- **THEN** the contract test fails and names the trait

#### Scenario: Unknown component name in the browser

- **WHEN** a widget arrives with a component name the browser code does not know
- **THEN** the widget shows an error naming that component
