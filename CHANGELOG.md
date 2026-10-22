# Changelog

## 0.6.3

This release ships the complete list of third-party licenses.

Fixed:

- `THIRD_PARTY_LICENSES.md` in the wheel lists every package that the frontend
  bundles include, with its notice. The 0.6.0, 0.6.1, and 0.6.2 wheels missed
  the Astryx themes and richtext, Lexical, and `@preact/signals-core`, and
  listed older versions of Astryx, Lumino widgets, React, and lucide-react.

## 0.6.2

This release fixes the workbench's charts, file dialogs, and menus in marimo.

Fixed:

- A Plotly chart in a workbench UI shows what `setup` added to it in marimo.
  Before, marimo drew the chart with empty axes, because the figure lost its
  traces before its frontend first rendered.
- The workbench's Export and Import dialogs open in marimo. Before, they did
  nothing when clicked.
- Clicking an option in a `Selector`, `DropdownMenu`, or `ContextMenu` selects
  it in marimo. Before, the click only closed the list. The frontend uses an
  Astryx canary build with the fix until Astryx releases it.

Added:

- `notebooks/marimo_workbench.py` opens the workbench with a real agent in
  marimo.

## 0.6.1

This release builds the workbench's UI in marimo, without waiting for a marimo
change.

Fixed:

- In a marimo cell, the workbench runs its turns on a `mo.Thread` that the cell
  starts, so the widgets a reply builds belong to that cell and close when it
  reruns. Before, building a reply's UI failed in marimo with an
  `AssertionError`. Outside marimo, such as in JupyterLab, nothing changes, and
  anylumino does not import marimo.

## 0.6.0

This release adds Astryx app frames, rich text, status widgets, and six
bundled themes, loads each frontend bundle once per page instead of once per
widget, and runs the widgets in marimo. Widgets now need a running kernel, so
read the breaking change below.

Breaking changes:

- Widgets load their frontend bundle from Python through a widget message, so
  they render only with a running kernel. A notebook saved with widget state
  no longer shows the widgets without one. In exchange, a page with 81 widgets
  uses about 35 MB of browser memory instead of 757 MB.

Added:

- Astryx widgets for app frames and navigation: `AppShell`, `Layout`,
  `TopNav`, `SideNav`, `NavIcon`, `HStack`, and `VStack`. A slot takes a list
  of widgets and stacks them.
- Astryx `Stepper`, `Timer`, `Indicator`, `OverflowList`, and
  `ComplexSelector`, and `Toast`, whose `notify` shows notifications from
  Python.
- `RichTextEditor` and `RichTextView`, which exchange Markdown.
- The workbench catalog and its component skill cover the new widgets.
- `BundledTheme` and the butter, chocolate, gothic, matcha, stone, and y2k
  Astryx themes: `ax.BuiltTheme(ax.BundledTheme.MATCHA)` needs no CSS path.
- Every widget class has a docstring example, and its API reference page shows
  a screenshot of it. `make docs-screenshots-components` captures them with
  Playwright.
- `notebooks/marimo_workbench_fake_agent.py` runs the workbench in marimo.
  Building a reply's UI there needs a marimo release that runs widget messages
  as part of the cell that created the widget; marimo 0.25.2 does not.

Fixed:

- `label_hidden` on `NumberInput`, `Slider`, `MultiSelector`, `DateInput`,
  `DateRangeInput`, `DateTimeInput`, `TimeInput`, and `ComplexSelector` was
  ignored, so an input inside a `Field` or `InputGroup` repeated its label.
- In marimo and other hosts without JupyterLab's Lumino stylesheet, inactive
  tabs of `TabPanel` and the other Lumino panels stayed visible and covered the
  selected one.
- `AppShell` no longer stretches to the window height inside a notebook output.

## 0.5.0

This release lets notebook skills add OpenUI components for their libraries'
widgets, and lets notebook code start, export, and import the workbench. The
export call changed, so read the breaking change below.

Breaking changes:

- `Workbench.export` takes the file path, such as
  `workbench.export("exports/sales.py")`, instead of a folder and a name.
  Exporting before a UI exists writes nothing and says so in the chat.

Added:

- A skill folder can hold a `components.py` whose `COMPONENTS` list adds
  OpenUI components, such as a chart widget from another library. The program
  lays them out like built-in components, the agent sees them in its prompt,
  and exported files import their modules.
- `Workbench(prompt=...)` sends a first chat message when the workbench is
  created, so a cell can start a turn.
- `workbench.import_file` accepts a string path, so another cell can import an
  exported file.
- `Table.columns` can be assigned after the table is created; the rows stay.

Fixed:

- An exported file no longer imports a name twice when the UI code and the
  callbacks both import it, such as `Event` from `anylumino.workbench`.

## 0.4.0

This release makes option values enums across the library and gives the
workbench's generated UI a cleaner contract. Both change user code, so read the
breaking changes below.

Breaking changes:

- Keywords that take a fixed set of values, such as `size`, `variant`, or
  `orientation`, now reject unknown values with a `ValueError` that lists the
  allowed ones. Before, an unknown value was passed to Astryx and rendered
  wrong without an error. Valid strings keep working.
- The workbench generates `UI` as a subclass of `anylumino.workbench.View`
  instead of `ax.Stack`. The root widget is `ui.widget`; anylumino containers
  and notebook cells still accept the `UI` itself. Statement names are now free
  except `app` and `widget`.
- Workbench handlers receive an `Event` with `source`, `value`, and `context`
  attributes instead of a dict: write `event.value`, not `event["value"]`.
- An `App` drives one UI: a second `UI(app)` raises `RuntimeError`.

Added:

- `StrEnum`s for the option values: 62 in `anylumino.astryx`, such as `Size`,
  `Density`, `ButtonVariant`, and `ColorMode`, and `Orientation`, `Direction`,
  `TabPlacement`, and `DockMode` in `anylumino`.
- `anylumino.workbench.Agent` for the agent CLIs, and the chat enums
  `ChatRole`, `MessageStatus`, and `ToolCallStatus` in `anylumino.astryx`.
- The workbench catalog reads option values from the enum annotations.

## 0.3.0

This release lets the workbench use a notebook's own libraries through
skills, and makes layout panels fit content that changes size, such as charts.

- Added `Workbench(skills=[...])` for skill folders in the Claude Code format,
  a `SKILL.md` with `name` and `description` front matter. The agent sees each
  skill's name and description and loads it when it needs it: Claude as a
  plugin for each turn, Codex by path. The skill paths are saved with the
  session.
- Layout panels with `fit_content` now follow their children: they refit when a
  child's content changes size, such as a chart frame that gains or loses
  panes, keep the fitted height instead of resetting to `height`, and split
  panels measure their panes like boxes, so they can also shrink.
- A container's `widgets` can be assigned objects that expose a `.widget`, such
  as a lightweight-charts `NotebookChart`, as the constructors already allowed.
- A click inside a layout panel no longer re-notifies children that are already
  shown, which reset a chart's visible range.
- Closing a workbench UI no longer fails on child widgets without a `widgets`
  trait, such as a chart's widget.

## 0.2.1

- GitHub releases now carry the version's changelog entry as their notes,
  instead of only a link to the compare view. The Release workflow stops
  before publishing when the changelog has no entry for the tagged version.

## 0.2.0

This release adds the workbench: build notebook UIs by chatting with a local
coding agent, then export them as plain Python.

- Added `anylumino.workbench.Workbench`, which builds notebook UIs by chatting
  with a local Claude Code or Codex CLI. The agent writes an OpenUI program and
  an `App` subclass with the callbacks; the workbench shows the live UI, the
  program, the generated Python, and the callbacks. Turns run read-only, named
  sessions resume the agent's conversation, and `model` and `effort` choose the
  agent's model and reasoning effort. The workbench needs `node` on `PATH`.
- The workbench catalog covers layout panels, cards, text, inputs, badges,
  tables, code blocks, Plotly figures through `Plot`, and namespace widgets.
  Handlers can fill an empty container for content that repeats per data item.
- Workbench **Export** writes one Python file with the OpenUI program, the `UI`
  class, and the `App` class. `anylumino.workbench.load(path, **namespace)`
  shows it in a notebook, and the file also imports as a module. **Import**
  reads an edited export back and asks the agent to reconcile a hand-edited
  `UI` class.
- Added `ax.Chat`, assembled from the Astryx chat components, with submit and
  stop events.
- Layout and tab panels refit when their container resizes, and a
  `fit_content` tab panel follows content changes.
- Added the `suppress_shortcuts` layout trait, so typing inside a panel does
  not trigger notebook shortcuts.
- Long Astryx chat system messages wrap instead of being clipped.

## 0.1.1

- Astryx value widgets now run `callbacks`, `on_click`, and `on_action` on every
  `value` change, matching the native date and time controls.
- Added a release workflow that builds the distributions, attaches them to the
  GitHub release, and publishes to PyPI from a `v*` tag.
- Published the documentation to GitHub Pages and linked it from the readme.
- Added runnable examples with screenshots to the documentation.

## 0.1.0

Initial public release.

- Lumino layout widgets: `TabPanel`, `SplitPanel`, `DockPanel`, `Toolbar`,
  `MenuBar`, and `CommandPalette`, composing child anywidgets through the
  anywidget 0.11 composition API.
- Astryx notebook components for inputs, layout panels, tables, surfaces, and
  overlays, with brand and theme wrappers and Python-backed search.
- Browser-native date, time, and datetime controls.
- Shared activation callbacks through `on_click`, `on_action`, and the
  `callbacks` constructor arguments.
- Rendering inside shadow DOM hosts such as marimo.
- Fumadocs documentation site with generated API reference pages.
- Documented the `uv` build, validation, TestPyPI, and PyPI release workflow.
- Added contributor setup and verification guidance.
