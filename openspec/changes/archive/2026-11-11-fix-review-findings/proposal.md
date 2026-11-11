# Proposal

## Why

A review of anylumino at `e0f611a` found 19 reachable defects across the layout widgets, the
Astryx widgets, the native pickers, and the workbench. Most share four causes: per-child state
that only one mutation path keeps aligned, a Python/JS contract that no test checks, three option
normalizers that disagree, and workbench entry points that each manage the running state by hand.
Fixing the defects without removing those causes leaves the next ones in place.

## What Changes

Layout widgets:

- Keep `stretches`, `sizes`, and `areas` aligned with children on move, reassignment, and add, as
  removal already does.
- Apply `spacing` in scrolling box panels.
- Honor the documented `separator` key in toolbars and menus.
- Scope command icons to their own widget.
- Report a bundle that never arrives instead of leaving every widget on the page blank.
- Stop importing a private anywidget function without a fallback.

Astryx widgets:

- `Table.append_row` and `prepend_row` work on tables with generated row ids. Row flags that the
  frontend reads (`selectable`, `enabled`) survive normalization, and setting `columns` keeps row
  data.
- **BREAKING** One option rule: every option value is a string on the wire, including bare
  scalars. `SelectionSlider([1, 2, 3]).value` becomes `"1"` instead of `1`, and
  `Selector([1, 5, 10])` renders instead of crashing.
- `Typeahead` and `Tokenizer` with a Python `search` keep and show the picked items.
- A child keeps its frontend state when its slot is hidden and shown, and its view is released
  when the slot goes away.
- `FileInput` shows the chosen file.
- Astryx `AccordionPanel` drops a removed child from its open keys and does not fire callbacks
  during construction.
- **BREAKING** Each attribute has one home. `label`, `variant`, `disabled`, and `icon` are read
  from their traits only; wrappers stop copying them into `props`. Constructor arguments that had
  no effect (`Pagination(disabled=...)`, `ContextMenu(disabled=...)`, `ButtonGroup(disabled=...)`,
  `Table(select_all_label=...)`) now work.
- **BREAKING** `ComponentWidget` loses the synced traits that no frontend view reads. The class
  and its export stay.
- The frontend component if-chain becomes a per-component table, split into modules by family. An
  unknown component name renders a visible error.

Native pickers:

- Fix the four defects in `DatePicker`, `TimePicker`, and `DatetimePicker`: date objects assigned
  after construction, malformed partial datetimes, stale popup selects, and listeners that are
  never removed.

Workbench:

- One turn lifecycle owns the running state, so a failure on any entry point leaves the workbench
  usable.
- A program with unresolved references is rejected instead of applied with parts missing.
- The first agent failure is the one reported; an early CLI exit reports its stderr.
- An explicit `cwd` overrides the saved one on a restored session.
- A workbench that takes over a session stops the turn still running on it.
- The component catalog reads constructor signatures instead of docstring text.

Guards:

- A contract test that fails when a synced trait is unread, a component name is unregistered, or
  a message type has no handler.
- Browser smoke tests for the frontend paths that only fail in a browser.
- `docs/openui.md` matches the shipped design.

## Capabilities

### New Capabilities

- `layout-composition`: keyed child composition in the Lumino layout widgets, including per-child
  metadata, scrolling, action widgets, and bundle loading.
- `astryx-widgets`: behavior of the Astryx component wrappers: options, tables, search inputs,
  child lifecycle, and how attributes reach the frontend.
- `native-pickers`: the date, time, and datetime picker widgets and their value contract.
- `openui-workbench`: adds turn recovery, session takeover, and working-directory override.
  `add-openui-workbench` introduces this capability and is not archived yet; archive it first so
  these requirements merge into its spec.
- `cli-agent-bridge`: adds failure reporting requirements. Same archive ordering.
- `openui-codegen`: adds unresolved-reference and malformed-child requirements, and the catalog
  source rule. Same archive ordering.

### Modified Capabilities

None. `openspec/specs/` is empty, so no archived requirement changes.

## Impact

- Python: `layout.py`, `components.py`, `controls.py`, `common.py`, `astryx/*.py`,
  `workbench/{workbench,agents,openui,codegen,catalog,session}.py`.
- Frontend sources: `static/layout/*.js`, `static/astryx/astryx_widget.js` (split into modules),
  `static/controls/native_control_widget.js`, `scripts/openui_tool.mjs`, and every generated
  bundle and loader.
- Public API: the three breaking changes above. `option_trader` notebooks that pass numeric
  options or read `SelectionSlider.value` as a number need the same update.
- Tests: new contract test, new browser test lane with a CI step that installs Chromium, and a
  regression test per finding.
- Docs: `docs/openui.md`, `CHANGELOG.md`, the regenerated API reference, and the checked-in
  workbench skill files.
- Dependencies: none added. `playwright` is already a dev dependency.
