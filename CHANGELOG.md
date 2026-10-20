# Changelog

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
