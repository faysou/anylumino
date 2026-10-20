# Tasks

## 1. anywidget render-after-attach fix (local clone)

- [x] 1.1 In `../anywidget`, create `fix/render-after-attach` from `origin/main`. Make
  `WidgetBinding.createView` in `packages/anywidget/src/binding.ts` wait for the target before it
  calls `render`: render at once if `target.el.isConnected`, otherwise await `target.displayed`,
  otherwise poll `isConnected` on `requestAnimationFrame` until the combined signal aborts. Verify
  with new tests in the clone's suite that cover the detached-then-attached, already-attached, and
  aborted-while-waiting cases.
- [x] 1.2 Apply the same wait to `host.getWidget(ref).render({el})` in
  `packages/anywidget/src/host.ts`. Verify with a test where a parent renders a child into a
  detached slot.
- [x] 1.3 Add `make install-dev-anywidget-local` to the anylumino `Makefile`. It builds the clone's
  frontend, runs `uv pip install -e ../anywidget`, and prints that later commands need
  `--no-sync`. Document it in `CONTRIBUTING.md`. Verify that
  `uv run --no-sync python -c "import anywidget; print(anywidget.__file__)"` points into
  `../anywidget`, and that `git diff pyproject.toml uv.lock` is empty.
- [x] 1.4 Reproduce issue #1025 in JupyterLab (`uv run --no-sync jupyter lab` from anylumino)
  with ego-lite: the Lumino `Widget.attach` widget from the issue, displayed 3 s after
  construction. Verify that it renders `attached` with the clone installed, and fails with PyPI
  anywidget 0.11.0.

## 2. Astryx Chat widget

- [x] 2.1 Add `Chat` to `src/anylumino/astryx/` and export it from `anylumino.astryx`, with these
  traits: `messages` (`role`, `content`, `status`, `tool_calls`), `is_streaming`, `placeholder`,
  and `disabled`. Add `on_submit` and `on_stop`, which handle the `submit` and `stop` messages.
  Add `submit` and `stop` to the message-contract test in `tests/test_widgets.py`. Verify with
  pytest tests that drive `_handle_frontend_message` and assert the exact callback arguments,
  including that a disabled chat ignores submit.
- [x] 2.2 Add the `Chat` case to `src/anylumino/static/astryx/astryx_widget.js`. It assembles
  `ChatLayout`, `ChatMessageList`, `ChatMessage` with `ChatMessageBubble` and Markdown,
  `ChatSystemMessage`, `ChatToolCalls`, and `ChatComposer` with stop while streaming. Put the pure
  message-to-props mapping in `astryx_bridge.mjs`. Verify with a `node --test` case for that
  mapping, and with `npm run build`.
- [x] 2.3 Add a `notebooks/astryx_chat.py` percent-format notebook with an echo bot that streams
  its reply. Verify with ego-lite in `uv run --no-sync jupyter lab`: messages render in order,
  streaming grows one bubble, stop appears and fires, and tool-call rows change status.
- [x] 2.4 Document `Chat` in the API reference and in the docs examples page. Verify that
  `make docs-check` passes.

## 3. OpenUI tool bundle

- [x] 3.1 Add `@openuidev/lang-core` and `zod` at exact versions to `package.json`, with the
  lang-core postinstall denied in `allowScripts`. Verify that `npm ci` runs no install script for
  them.
- [x] 3.2 Add `scripts/openui_tool.mjs` with the `parse`, `merge`, and `prompt` commands, which
  read JSON on stdin and write JSON on stdout. Add a `platform: "node"` entry in
  `scripts/bundle-entries.mjs` that outputs
  `src/anylumino/static/openui/openui_tool.bundle.mjs`. Verify that `npm run build` produces it
  and that the wheel includes it.
- [x] 3.3 Copy a few OpenUI 1.0 conformance fixtures (grammar, actions custom, editing, errors)
  with their MIT notice into `tests/frontend/fixtures/openui/`, and add `node --test` cases that
  run the bundle on them. Verify that each `expected.json` tree and merged program matches.

## 4. Catalog and system prompt

- [x] 4.1 Add `src/anylumino/workbench/catalog.py` with the components listed in the
  `openui-codegen` spec and the `Callback` action, and a function that emits the OpenUI
  LibrarySpec JSON. Verify with a test that asserts the exact component list and prop order, and
  with a test that builds every entry's anylumino class from sample props.
- [x] 4.2 Add `src/anylumino/workbench/openui.py`, which runs the bundle with
  `asyncio.create_subprocess_exec("node", ...)`, and raises an error naming `node` when it is
  missing. Verify with pytest: one parse of the catalog library, one merge, one prompt, and the
  missing-`node` error with an empty `PATH`.
- [x] 4.3 Generate the system prompt with inline mode and edit mode on, and bindings and tools
  off. Add the callback contract and the namespace summary, and cache the prompt by catalog hash.
  Verify with tests that the prompt contains every component and `@Callback`, does not contain
  `Query(`, `Mutation(`, or `$`-variables, and stays below a measured size bound.

## 5. Code generation and callbacks

- [x] 5.1 Add `src/anylumino/workbench/codegen.py`, which turns a parsed tree into the `build`
  module described in `design.md`. Verify with an exact-source snapshot test for a program that
  uses each catalog component kind, and with a determinism test.
- [x] 5.2 Generate callback wiring for `@Callback` and `@ToAssistant`, using the event the catalog
  assigns to each action slot. Verify with tests that exec the generated module and fire a button
  click and an input change through `_handle_frontend_message`, and assert the exact `event` dicts
  and `ask_agent` calls.
- [x] 5.3 Add named generation errors for a dynamic prop, an unknown handler, a missing namespace
  widget, and unsupported features (`$state`, `Query`). Verify with one parametrized test that
  asserts each error message.

## 6. CLI agent bridge

- [x] 6.1 Add reply splitting into prose, an optional `openui` fence, and an optional `python`
  fence, and reject duplicate fences. Verify with a parametrized pytest covering both fences, only
  `openui`, only `python`, neither, and duplicates.
- [x] 6.2 Add the Claude runner. Settle the `--permission-mode` open question from `design.md`
  by checking against 2.1.302, record the answer in `design.md`, and add the runner with first
  and resume arguments, stream parsing, and the read-only tool list. Capture a real stream once
  into `tests/fixtures/agents/claude/`. Verify with a fake `claude` on `PATH` that replays it, and
  assert the argv, the text deltas, the tool calls, and the session ID.
- [x] 6.3 Add the Codex runner. Settle the codex system-prompt open question from `design.md`,
  record the answer there, and add the runner with `exec` and `exec resume` arguments, the
  read-only sandbox, and JSONL parsing. Capture a real stream once into
  `tests/fixtures/agents/codex/`. Verify with a fake `codex` that replays it, and assert the argv,
  the text, the items, and the thread ID.
- [x] 6.4 Add the one-turn-at-a-time guard, stop (SIGTERM to the process group, then SIGKILL after
  a grace period), and the missing-executable error. Verify with tests that use a fake CLI that
  sleeps: a second submit starts nothing, stop exits within the grace period, and the error names
  the executable.

## 7. Session store

- [x] 7.1 Add `src/anylumino/workbench/session.py`, which saves and loads
  `~/.anylumino/sessions/<name>.json` with an atomic write, validates names, and holds the fields
  listed in the `openui-workbench` spec. Verify with tests under a temporary `HOME`: an exact
  round-trip of every field, and rejection of `../x`.

## 8. Workbench assembly

- [x] 8.1 Add `src/anylumino/workbench/workbench.py` with `Workbench(agent="claude", session=None,
  namespace=None, cwd=None)`. Build the split, the header, the chat, and the four keyed tabs with
  read-only `CodeBlock`s and the empty `UI` state. Export it from `anylumino.workbench`. Verify
  with a pytest that asserts the tab keys and titles, the selected `ui` tab, and the header text.
- [x] 8.2 Wire submit -> bridge turn -> streamed chat updates -> atomic apply -> tab updates, with
  stop, `ask_agent`, and callback errors shown as system messages. Verify with pytest using the
  fake CLIs: a successful turn updates all four tabs, a callbacks syntax error leaves all four
  unchanged with an error naming the line, and a raising handler is reported while other handlers
  still run.
- [x] 8.3 Wire session save after each turn and restore when the workbench is created, including a
  restore where the UI cannot be built. Verify with pytest: two turns, a new `Workbench` with the
  same session gives equal tab contents and messages, and the next turn uses resume arguments.
- [x] 8.4 Add a `notebooks/openui_workbench.py` example with a `sales` data frame in the
  namespace, and a docs page covering setup (`node`, `claude` or `codex`), the four tabs, the
  callback contract, sessions, and the trust model for executed code. Verify that `make docs-check`
  passes and that the notebook runs with `uv run --no-sync`.

## 9. Integration checks

- [x] 9.1 With the clone installed (1.3), start `uv run --no-sync jupyter lab` from anylumino and
  drive `notebooks/openui_workbench.py` with ego-lite. Check that the layout renders, the tabs
  switch, typing in the code tabs does nothing, and a fake-agent turn updates all four tabs.
  Capture screenshots under `build/review/`.
- [x] 9.2 Run one live turn with `claude` and one with `codex` in that notebook, and only when the
  user asks, since they spend tokens. Check that each builds a UI whose button runs its callback
  against `sales`, and that restarting the kernel and restoring the session resumes the agent.
  Ran on 2026-10-19 through the `Workbench` API with the notebook's `sales` namespace, not in a
  browser: both agents passed.
- [x] 9.3 Run `make test`, and check that CI-equivalent `uv sync --group dev && uv run pytest`
  passes with PyPI anywidget, without the clone.

## 10. Component options

- [x] 10.1 Derive an `options` object prop for each catalog component from its wrapper's keywords,
  pass the options as keywords in generated code, and reject unknown options. Verify with pytest:
  the Table option types, the parser type check, and the codegen snapshot with `sortable`.
- [x] 10.2 Generate the `openui-components` skill into the package plugin directory with
  `make workbench-skill`, and point the system prompt to it. Verify with pytest that the files
  match the catalog and that the prompt does not list the options.
- [x] 10.3 Load the plugin in `claude` with `--plugin-dir` and allow the read-only tools with
  `--allowedTools`. Verify with one live turn per CLI that the agent reads `Table.md` and the
  reply builds a sortable table.
- [x] 10.4 Keep the user's MCP servers out of turns: `--strict-mcp-config` for `claude`, and one
  `enabled=false` override per server from `codex mcp list --json` for `codex`. Verify with pytest,
  and with the `claude` init event, which lists only `Read`, `Grep`, `Glob`, and `Skill`.
- [x] 10.5 Derive enum values for string options from the wrapper's numpydoc value sets, then from
  the Astryx prop literals of the prop each keyword is passed to, read from the wrapper source.
  List the Table `selects` and `sort_direction` values and the Stack `align` and `justify` values
  as numpydoc sets. Verify with pytest that the parser rejects `density: "tight"` and that renamed
  props, `; default` suffixes, and wrapped entries yield their values.
- [x] 10.6 Add the `setup(widgets)` callback, teach it with `set_rows` and `items` in the system
  prompt, and reserve `python` fences for callbacks. A live turn before this asked the user to
  paste the data frame rows and sent two `python` blocks. Verify with pytest and with the live
  9.2 turns.
- [x] 10.7 Show the status as a visible caption next to the header's `StatusDot`, whose label
  Astryx gives only to screen readers, in an Astryx stack so the items keep their natural widths.
  Dispose the action panel through `disposeLuminoWidget`. Verify with pytest that the caption
  reads `Running` during a turn.
- [x] 10.8 Fix the browser findings: layout and tab panels refit on a container resize through a
  `ResizeObserver`, not only on a window resize; the workbench sets the new `suppress_shortcuts`
  layout trait so keys in a code tab do not act as notebook shortcuts; the user message, not
  the finished reply, carries the `sent` status; and a `fit_content` tab panel follows content
  changes and measures through box-less mount roots wherever the panel is scrolled. Verify with pytest, `node --test`, and an ego lite
  recheck in JupyterLab.

## 11. Export and load

- [x] 11.1 Move running the callbacks and the UI code out of `Workbench.apply` into
  `src/anylumino/workbench/export.py`, and add `load(ui, callbacks, namespace=None)` there,
  exported from `anylumino.workbench`. Verify with pytest: a loaded fake-agent UI fires a button
  callback against a `__main__` global and runs `setup`, and `ask_agent` warns.
- [x] 11.2 Add the `Export` header button and the folder dialog: a path, an up button, one button
  per subfolder, a name input, and `Cancel` and `Export`. Verify with pytest that it browses a
  temporary tree, writes both files equal to the tabs, and posts the `load` call; and with ego lite
  in JupyterLab that the dialog opens, browses, exports, and a `load` cell shows the same UI.
- [x] 11.3 Document export and load on the workbench page. Verify that `make docs-check` passes.

## 12. App and UI classes

- [x] 12.1 Add `App` in `src/anylumino/workbench/app.py`, a plain class with `set_ui`, `setup`,
  `call`, `ask_agent`, and namespace keywords, exported from `anylumino.workbench`. Verify with
  pytest: namespace attributes, rejected names, `on_error`, and the detached `ask_agent` warning.
- [x] 12.2 Generate a `UI(app)` widget class with attribute widgets, find the single `App`
  subclass in the callbacks, run the callbacks without globals, and show the UI in the `UI` tab.
  Teach the contract in the system prompt. Verify with the updated codegen snapshot and workbench
  tests, and with tests that a handler replacing an `App` member and a statement named after a
  widget member are rejected.
- [x] 12.3 Change `load` to `load(ui, callbacks, **namespace)` returning the UI, and put the
  namespace keywords in the export message. Verify with pytest, with a test that imports the
  exported files as modules and composes two UIs in an `al.TabPanel`, and with ego lite in
  JupyterLab.
- [x] 12.4 Update the fake-agent notebook, the workbench docs, and the screenshots. Verify that
  `make docs-check` passes.
- [x] 12.5 Export one module `<name>.py`, the UI code then the callbacks, with the callbacks'
  imports moved up, and change `load` to `load(path, **namespace)`. Verify with pytest, including
  the joined source and importing the module, and with a live Claude Code turn exported and
  loaded.

## 13. Review fixes

- [x] 13.1 End a turn with a system message on any agent failure, refuse a second submit before
  the agent starts, update the turn's reply by index, and send an apply error only with the next
  turn. Verify with pytest: unreadable agent output, a double submit, a message posted mid-turn,
  and prose-only turns after a failed apply.
- [x] 13.2 Put the callbacks' `__future__` imports first in an export, reject callbacks that bind
  `UI`, `al`, or `ax`, give a UI without handlers an empty `App` subclass, and default the export
  name to an importable session name. Verify with pytest.
- [x] 13.3 Raise when a restored session gets another agent, close the previous UI's widgets
  except namespace widgets, and let a stop before the agent process starts cancel the turn. Verify
  with pytest.
- [x] 13.4 Wrap long chat system messages and post the export message as an assistant message.
  Verify in JupyterLab with ego lite.

## 14. Charts

- [x] 14.1 Add a `Plot(layout?)` catalog component that builds an empty Plotly `FigureWidget` when
  Plotly is installed, import Plotly in generated code only when a program uses it, and drop
  imports the callbacks repeat when exporting. Verify with a codegen snapshot test, an export
  test, a live Claude Code turn that builds two charts without a namespace figure, and JupyterLab.
- [x] 14.2 List the column types of data frames in the namespace summary. Verify with pytest.
- [x] 14.3 Teach the agent to fill an empty container from a handler for content that repeats per
  data item, and to keep state in the app instead of OpenUI `$variables`, `Query`, `Mutation`, and
  `@Each`. Give each component's skill file its Python constructor. Document the Node requirement.
  Verify with pytest and a live Claude Code turn that builds one chart and one card per product.
- [x] 14.4 Add `model` and `effort` workbench arguments, passed to Claude Code as `--model` and
  `--effort` and to Codex as config overrides on every turn, saved with the session and shown in
  the header. Verify with pytest and a live Codex turn that builds one chart and one card per
  product.
- [x] 14.5 Show line numbers in the three code tabs. Verify with pytest, in JupyterLab, and with
  retaken documentation screenshots.
- [x] 14.6 Export the OpenUI program as a comment with a fingerprint of the `UI` class, and add an
  `Import` button and dialog that read an exported file back. Apply unchanged files, edited
  callbacks, and edited programs directly, and send files with an edited `UI` class or that do not
  apply to the agent to reconcile, then report whether the reconciled `UI` class matches the file.
  Verify with pytest, in JupyterLab, and with a live turn that reconciles an edited `UI` class.

## 15. Notebook skills

- [x] 15.1 Add `Workbench(skills=[...])` for skill folders with a `SKILL.md`, list them in the
  system prompt, load them in Claude as a per-turn plugin with read access to their folders, and
  save them with the session. Verify with pytest.
- [x] 15.2 Accept objects that expose a `.widget`, such as a lightweight-charts `NotebookChart`,
  when a container's `widgets` is assigned, and close such children with the previous UI. Verify
  with pytest.
- [x] 15.3 Write a `lightweight-charts` skill and a `workbench_chart_replay.py` notebook in
  option_trader that rebuild the delta hedge dashboard from its chart catalog. Verify with a live
  Claude Code turn and in JupyterLab.
- [x] 15.4 Make `fit_content` layout panels follow their children: keep the fitted height when the
  panel's own resize observer fires, measure split panes like boxes, and refit when a child's
  content changes size. Fit `LiveDashboard` in option_trader with it instead of setting heights
  from Python. Verify with `node --test`, the chart explorer, and a `LiveDashboard` replay in
  JupyterLab.
- [x] 15.5 After a click inside a layout panel, render only children the click revealed, so an
  already shown chart keeps its view instead of resetting through a resize notice. Verify with
  cycle-row clicks in the chart explorer.
