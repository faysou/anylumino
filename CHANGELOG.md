# Changelog

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
