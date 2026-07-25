# Astryx Notebook Review

Review of the astryx notebooks (`astryx_components_smoke.py`, `astryx_table.py`, `astryx_themes.py`)
rendered in JupyterLab, plus a code review of the component communication design. Date: 2026-07-24.
Method: ran `uv run jupyter lab`, executed all cells through a browser in light and dark JupyterLab
themes, verified findings against the live DOM, then traced each defect to source. Analysis only; no
code was changed.

## Summary

The table notebook renders well and Python callbacks work end to end. One Python bug in child
normalization explains most of the broken visuals in the smoke and themes notebooks. Five
independent rendering defects follow it, and the communication layer is sound in design but has
robustness and consistency gaps.

## Appearance findings

Ordered worst first.

1. `Field` / `InputGroup` lose their wrapped input. "Wrapped symbol" and "Quantity" render only
   label, description, and the `sh` suffix; no input with value `NVDA` or `100` exists in the DOM.
   Root cause is Python: `_normalize_children` (`layout.py:111-131`) calls `list(children)` on a
   single widget; `ComponentWidget` has `__getitem__` but no `__iter__`, so legacy iteration turns a
   childless input into `[]` and a container into its grandchildren, silently reparenting them.
   Mapping children never iterate, which is why `Tooltip` and `Popover` triggers work. Fix: wrap a
   single widget in a list before normalizing, and give `ComponentWidget` an `__iter__` that raises.
2. Dark theming breaks twice over. In `astryx_themes.py`, the `mode="dark"` and `mode="system"`
   panels show pale dark-mode text on a white background and a near-black progress track. Primary
   cause is finding 1: `ax.Theme(card, ...)` flattens the single `Card` away, so the dark card
   surface never mounts while its children still receive dark foreground tokens. Structural issues
   remain after that fix: each anywidget is its own React root, so every widget mounts a root
   `<Theme>` that writes `html[data-theme]` globally (last mount wins, unmount clears it), and the
   upstream runtime brand CSS dedupe removes the shared style tag when the first injecting widget
   unmounts, stripping brand tokens from survivors.
3. Dropdowns open detached from their trigger. The Metric selector at x=1500 opened its listbox at
   x=643. Astryx positions overlays with CSS anchor positioning keyed by React `useId`, and
   anylumino creates one React root per widget with no `identifierPrefix`
   (`astryx_widget.js:1547`), so anchor names collide across widgets and the popover anchors to
   another widget's trigger. Fix: `createRoot(el, {identifierPrefix: <model_id>})`; this also fixes
   duplicate DOM ids.
4. JupyterLab dark theme is ignored. With Lab in dark mode the whole output stays white;
   `mode="system"` follows only the OS `prefers-color-scheme`. Nothing reads
   `body[data-jp-theme-light]`. A `"jupyterlab"` mode is cheap: resolve light/dark from that
   attribute plus a shared MutationObserver, and pass the resolved mode to `<Theme>`.
5. `Grid(columns="repeat(auto-fit, ...)")` silently becomes one column. Astryx `Grid` accepts only a
   number or a `{minWidth, repeat}` mapping; a string falls through to `1fr`. The wrapper
   (`surfaces.py:212`) declares the narrower type but forwards strings unvalidated. Translate the
   common `repeat(auto-fit, minmax(Npx, 1fr))` form or raise a `TypeError`.
6. `ProgressBar` label collides with its value: "Render coverage58%" (measured gap 0px). The header
   uses `justify-content: space-between`, but the host CSS gives slots no width, so in shrink-to-fit
   contexts such as a horizontal `Stack` the free space is zero. Fix in `astryx_widget.css`:
   `width: 100%` or `align-self: stretch` on child hosts.
7. `StatusDot("Connected")` drops its label; only the dot renders and the text appears nowhere in
   the DOM. Not root-caused; it sits in mapping children, so it is not finding 1. Check the
   StatusDot prop mapping.
8. Smoke notebook layout problems, partly notebook and partly library:
   - The visuals grid leaves a large blank region: the tall "structure" card lands alone in row 2 of
     a 4-column grid.
   - `CommandPalette(width=420)` and `Dialog(width=360)` overflow their ~300px grid column and clip
     (the palette footer and the alert dialog's confirm button are cut off).
   - The `Overlay` ghost button clips to "uick vie" inside the tiny default `Thumbnail`.
   - The slider value "42" clips at the column edge.
   - Two identical adjacent "..." buttons (`MoreMenu`, `IconButton`) and two "Apply" buttons read as
     duplicates.
   - Checked `CheckboxList` items get heavy filled boxes while `RadioList` stays plain, which looks
     inconsistent.
   - The bottom `status` TextWidget centers itself and looks detached from the panel above.
9. Scroll-mode ergonomics: the resize handle is absolutely positioned inside the scroll container
   and scrolls out of view in `scroll=True` panels; hosts that cap output height (VS Code) get
   nested scrollbars; third-party children that position popups in-subtree clip at the `overflow`
   boundary.

## Code and communication review

The core design is sound: children sync as `"anywidget:<model_id>"` refs resolved through
`host.getWidget` with an ipywidgets fallback, mutations batch under `hold_sync`, listeners and React
roots are cleaned up on abort, and the owner-wrapper pattern (`panel["key"]` returns the owner,
`.widget` the view) avoids name collisions by construction.

Improvements, ranked:

1. Render failures are silent and contagious. A child render that throws leaves the
   `anyluminoRendering` flag stuck and, because siblings render sequentially, blanks every later
   child with no error placeholder (`layout_panel.js:357-398`). Wrap per-child, reset the flag in
   `finally`, and show an inline error.
2. Every mutation rebuilds everything, twice. `change:widgets` and `change:child_keys` both trigger
   full teardown and rebuild, so `add_widget` or a title rename remounts all children (iframes
   reload, plots redraw, focus lost). Coalesce the events and go incremental. The astryx side
   over-renders the same way: 24 traits funnel into a `flushSync` that aborts and remounts all child
   widgets on any parent trait change (`astryx_widget.js:1550-1585`).
3. `tabs_movable` is half implemented. The frontend honors it but never syncs tab moves back, so
   after a drag `selected_key` maps to the wrong child and any rerender snaps tabs back. Sync
   Lumino's tab-move signal or remove the option.
4. Three callback idioms coexist: `_ActionWidget` constructor-only dicts (`layout.py:1054-1071`),
   `ComponentWidget` `on_click`/`on_action` lists (`components.py:114-138`), and
   `_NativeControlWidget` anonymous observe lambdas that can never be unregistered
   (`controls.py:33-40`). A `click` message carrying a value also fires both `on_action` and
   `on_click`. Converge on one registration and removal idiom, and document `traitlets.link` and
   `observe` as the blessed sibling-state pattern; a state store is not needed.
5. Wasted and unbounded traffic. `setModelValue` (`astryx_widget.js:257-261`) sends both a trait
   update and a `"change"` custom message nobody consumes, per keystroke, and no
   `continuous_update` or debounce option exists for text inputs or sliders.
6. Fragile slot matching. Astryx children pair `refs[index]` with `querySelectorAll(...)[index]`,
   but component DOM order (Toolbar start/center/end) need not match key order. The slots already
   carry `data-anylumino-index`; query by it.
7. Lifecycle gaps. `remove_widget` never closes child models, so they accumulate in the ipywidgets
   registry, and it does not shrink `SplitPanel.sizes`, leaving the trait inconsistent with
   `child_keys`. Construction-time-only wiring means assigning `widget.widgets = [...]` later
   bypasses owners, brand propagation, and key generation.
8. Duplication and API asymmetries. `ComponentWidget` re-implements keyed access with subtly
   different semantics than `LayoutWidget` (`0 in panel` is False while `panel[0]` works;
   whitespace handling differs). Share a keyed-children mixin and raise KeyError-style messages that
   name the key. The frontend duplicates `clampIndex`, `titleFor`, and fit-content logic across
   `layout_panel.js`, `tab_panel.js`, and `action_panel.js`.
9. Test gap. Python model tests cover serialization, keyed access, and owners well, but all
   composition, teardown, and scroll behavior lives in the frontend and only
   `astryx_bridge.test.mjs` exists. Finding 1 deserves a regression test for
   `Field(TextInput(...))`.

## Notebook quick wins

Until the library fixes land:

- Pass list or mapping children everywhere: `ax.Field([ax.TextInput(...)])` and
  `ax.Theme([card], ...)` render correctly today.
- Use the mapping form of `Grid.columns` in `astryx_themes.py`.
- In the smoke notebook, give the palette, dialog, and alert their own full-width section instead of
  a 300px grid cell, drop one of the duplicated Apply buttons, and give the two "..." menus distinct
  labels.
- End row-helper cells with a semicolon, or have the helpers return `None`, so `'AMD'` and `'TSLA'`
  echoes stop cluttering `astryx_table.py`.

## Suggested fix order

1. Wrap single-widget children in `_normalize_children` (fixes findings 1 and the main symptom of
   2, likely also the context for 6).
2. Pass `identifierPrefix` to `createRoot` (fixes finding 3 and duplicate ids).
3. Validate or translate `Grid.columns` strings (finding 5).
4. Widen the child host CSS (finding 6).
5. Frontend-side theme inheritance plus an `html[data-theme]` sync guard, then the `"jupyterlab"`
   mode (findings 2 and 4).
