# Tasks

Finding numbers (F1 to F19) refer to the review at `e0f611a`. Every task that edits a frontend
source ends with `npm run build`, and is done when `npm test` passes and
`git status --short src/anylumino/static` lists only intended files.

## 1. Browser test lane

- [x] 1.1 Move the `jupyterlab()` context manager and notebook runner from
  `scripts/docs_examples.py` into an importable module both can use; verify
  `make docs-screenshots-components` still captures.
- [x] 1.2 Add `tests/browser/` with a `browser` pytest marker excluded by default, a session
  fixture that starts one JupyterLab and Chromium, and `make test-browser`; verify `uv run pytest`
  collects no browser test and `make test-browser` runs one that displays `al.TextWidget("x")`.
- [x] 1.3 Add a smoke test that renders every Astryx component and every layout widget from
  `notebooks/astryx_components_smoke.py` and asserts no error node and no console error; verify
  it passes on the unchanged code.
- [x] 1.4 Add a CI step that installs Chromium and runs `make test-browser`; verify the workflow
  file passes `actionlint` or a dry read, and document the lane in `CONTRIBUTING.md`.

## 2. Layout composition

- [x] 2.1 (F7) Add the per-child trait list and the single permutation method to `KeyedChildren`
  per design D2, route `add_widget`, `remove_widget`, `move_widget`, and `_rekey_children` through
  it, and delete `_drop_child_metadata`; verify with parametrized tests for `BoxPanel.stretches`,
  `SplitPanel.sizes`, and `GridPanel.areas` covering move, reassignment, add, remove, the frontend
  `move` message, and the empty-list case.
- [x] 2.2 (F16) Apply numeric `spacing` to the scroll box gap; verify with a browser test that
  measures a 20 pixel gap for `BoxPanel(scroll=True, spacing=20)`.
- [x] 2.3 (F17) Use one separator predicate in the toolbar and menu builders; verify with a
  browser test for both documented spellings and correct the `Toolbar` and `MenuBar` docstrings.
- [x] 2.4 Scope command icon classes and the icon observer to the widget per design D13; verify
  with a browser test that two menu bars sharing an action id show different icons.
- [x] 2.5 Add the bundle load timeout and failure message to the loader template in
  `scripts/build-frontend.mjs`; verify with a `node --test` case that a request with no answer
  rejects, clears the shared promise, and a second request succeeds.
- [x] 2.6 Wrap the private anywidget import so a failure raises an `ImportError` naming the
  anywidget version; verify with a test that patches the import to fail.

## 3. Options and tables

- [x] 3.1 (F4, F15) Stringify scalar options in `_option_records` and take the `SelectionSlider`
  default from the record; verify with tests that `Selector([1, 5, 10]).props["options"]` holds
  string values and `SelectionSlider([1, 2, 3]).value == "1"`, and a browser test that the
  numeric `Selector` renders and a slider drag yields `"2"`.
- [x] 3.2 Update every anylumino notebook, docs example, and `option_trader` caller that passes
  non-string scalar options or reads a numeric option value; verify with `uv run pytest
  tests/test_examples.py` and the `option_trader` tests that import anylumino.
- [x] 3.3 (F1) Number a generated row id from the existing rows in `_normalize_new_row`; verify
  with tests for append and prepend on mapping rows without ids, on sequence rows, and for the
  explicit duplicate id error.
- [x] 3.4 (F13) Keep full row data in the table and send row flags to the frontend; make the
  `columns` setter read from the kept rows; verify with tests for a `selectable: False` row
  outside the columns and for widening `columns`, and a browser test that the row cannot be
  selected.

## 4. Astryx contract and structure

- [x] 4.1 Route every frontend trait read through one accessor and add the contract test per
  design D6, with the currently unread traits and unhandled messages listed as expected failures;
  verify the test names exactly the gaps from F12.
- [x] 4.2 Move `componentProps`, `componentChildren`, and the name registries into the `SPECS`
  table under `static/astryx/components/` with no behavior change; verify the smoke test from 1.3
  passes before and after and the bundle file names are unchanged.
- [x] 4.3 Render a visible error for a component name missing from `SPECS`; verify with a browser
  test that sets an unknown `component_name`.
- [x] 4.4 (F12) Make the trait the only source of `label`, `variant`, `disabled`, and `icon`:
  stop wrappers copying them into `props` and read the traits in each spec, including
  `Pagination`, `ContextMenu`, `ButtonGroup`, `DropdownMenu`, `IconButton`, and
  `Table.select_all_label`; verify by removing the matching expected failures from 4.1 and with a
  browser test that assigning `DropdownMenu.label` after display updates the button.
- [x] 4.5 Remove each `ComponentWidget` synced trait the contract test still reports as unread,
  keeping the class and its export; verify the contract test passes with no expected failures and
  `tests/test_widgets.py` passes.
- [x] 4.6 (F14) Prune removed children from the Astryx `AccordionPanel` open keys and set its
  initial value before callbacks register; verify with tests for both scenarios in the spec.
- [x] 4.7 Regenerate the API reference and the workbench skill files; verify `make docs-check`
  passes and the skill diff shows only the removed traits and changed option types.

## 5. Astryx child lifecycle and inputs

- [x] 5.1 (F6) Write browser tests for a `SplitPanel` child inside an unselected Astryx
  `TabPanel` and for an inline `Dialog` reopened ten times, asserting render count and live view
  count; verify they fail on the current code, or record the finding as rejected here.
- [x] 5.2 (F6) Give each Astryx child slot its own abort controller and keep hidden slots mounted
  per design D7; verify the tests from 5.1 pass and the smoke test from 1.3 passes.
- [x] 5.3 (F5) Write browser tests with a Python `search` for a `Typeahead` pick, two `Tokenizer`
  picks, and a trait change during a slow search; verify they fail on the current code, or record
  the finding as rejected here.
- [x] 5.4 (F5) Add the item cache and memoized search source per design D8; verify the tests from
  5.3 pass.
- [x] 5.5 (F9) Show the chosen file in `FileInput`; verify with a browser test that sets a file
  on the input and reads the displayed name and the kernel `value`.
- [x] 5.6 Check in a browser whether `Popover`, `Tooltip`, and `HoverCard` widget content mounts
  when Astryx portals the layer; verify with a browser test per component, and fix the content
  lookup in this task if a test fails.

## 6. Native pickers

- [x] 6.1 (F8) Validate `value`, `min`, and `max` to an ISO string or `None` on every assignment;
  verify with a parametrized test over the three pickers that assigns `date`, `time`, and
  `datetime` objects and serializes the state with `json.dumps`.
- [x] 6.2 (F8) Sync a `DatetimePicker` value only when date and time are both present, and keep
  seconds on a date edit; verify with `node --test` cases for the value composition function
  covering the three partial inputs and the seconds case.
- [x] 6.3 (F8) Read the popup hour and minute from the current value when the popup opens; verify
  with a browser test that assigns `"09:45"` from Python, picks hour 10, and reads `"10:45"`.
- [x] 6.4 (F8) Use `signal` and `modelListeners` in `native_control_widget.js`, remove document
  listeners on rebuild and disposal, and re-render on `continuous_update`; verify with a browser
  test that counts document listeners after twenty `disabled` toggles and after clearing the
  output.
- [x] 6.5 Correct the picker docstrings to state the ISO string value contract; verify
  `make docs-check` passes.

## 7. Workbench turn lifecycle

- [x] 7.1 (F2, F19) Add the turn context manager per design D9 and run `submit`, `ask_agent`,
  `import_file`, and `restore` inside it; verify with tests that a non-UTF-8 import and an
  injected unexpected error each leave `running` false, post a system message, and accept the
  next submit.
- [x] 7.2 (F19) Record one outcome per turn, finalize tool call statuses, and make
  `report_reconcile` read the outcome; verify with tests for a failed reconcile turn (one
  message) and a stopped turn (no tool call left `running` in chat or in the saved session).
- [x] 7.3 Check stop at every await boundary of a turn; verify with a test that stops between the
  agent reply and apply and asserts the UI is unchanged.
- [x] 7.4 (F10) Keep the first `Failed` event; verify with a fake CLI that emits an error result
  and exits 1, asserting the chat shows the error text, and one that exits 2 with stderr only.
- [x] 7.5 (F18) Start the stderr reader before writing the prompt and treat a broken stdin pipe
  as an early exit; verify with a fake CLI that exits at once with stderr text and a 4 MB prompt.
- [x] 7.6 (F11) Let an explicit `cwd` override the saved one and save it; verify with tests for
  both spec scenarios and update the `Workbench` docstring.
- [x] 7.7 Add the session registry and takeover, and cancel the pending turn before the marimo
  loop closes; verify with a test that creates a second workbench on a session with a running
  fake turn and asserts the first process ended and one result was saved.
- [x] 7.8 Lock chat message updates; verify with a test that calls `add_message` and
  `update_reply` from two threads 1,000 times and asserts no message is lost.
- [x] 7.9 Give the shared `agent_reply` fixture in `tests/conftest.py` a Claude-format variant
  and parametrize the workbench turn tests over both agents; verify both variants run.

## 8. OpenUI results, codegen, and catalog

- [x] 8.1 (F3) Return typed results from `openui.py` per design D10 and reject unresolved
  references in `apply`; verify with tests for an undefined component reference and an unquoted
  callback handler, each asserting an unchanged UI and an error naming the reference.
- [x] 8.2 (F19) Raise a `GenerationError` naming the statement for a child that is not a
  component; verify with a test for `box = VBox(["hello"])`.
- [x] 8.3 Build catalog props and option values from resolved annotations and move the Astryx
  prop renames and pass-through unions into per-wrapper declarations per design D12; verify with
  a test that rewrites a docstring's descriptions and gets an equal catalog entry.
- [x] 8.4 Extend `test_catalog_entry_builds_its_class` to build each component once per listed
  option value; verify it passes.
- [x] 8.5 Regenerate the workbench skill files with `make workbench-skill`; verify the diff
  against the committed files loses no prop and no option value.
- [x] 8.6 Rewrite `docs/openui.md` to describe the `UI(View)` class design and the OpenUI Lang
  parser; verify every code sample in it runs through `tests/test_examples.py`.

## 9. Release integration

- [x] 9.1 Add the 0.7.0 CHANGELOG entry with a migration section for the three breaking changes,
  each with before and after code; verify `uv run pytest tests/test_release_notes.py` passes.
- [x] 9.2 Run `make test`, `make test-browser`, and `make docs-check`, then `npm run build` and
  `npm run licenses`; verify all pass and `git diff --exit-code -- src/anylumino/static
  THIRD_PARTY_LICENSES.md` reports no change after the rebuild.
- [x] 9.3 Run the `option_trader` test suite and its notebooks that import anylumino against this
  branch; verify they pass.
  - Done with limits: the 258 tests pass, and `workbench_chart_explorer_check.py` runs.
    `workbench_chart_replay.py` stops before any anylumino code because its local DuckLake
    chart catalog needs a layout migration, and the Databento notebooks need the Databento API;
    neither ran.
- [x] 9.4 Run `notebooks/component_examples.py` and the workbench notebook with the fake agent in
  JupyterLab and in marimo; verify each renders with no error output.

## Workflow follow-up

- Archive `add-openui-workbench` before this change, so the workbench deltas merge into its specs.
- Archive this change after 9.x passes and the release is tagged.
