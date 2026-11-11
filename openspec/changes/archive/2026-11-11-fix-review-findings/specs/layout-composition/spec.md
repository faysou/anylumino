# Spec Delta

## Purpose

Lumino layout widgets that compose child widgets by key, keep per-child settings attached to the
right child through every mutation, and render action widgets such as toolbars and menus.

## ADDED Requirements

### Requirement: Per-child settings follow their child

A layout widget SHALL keep each per-child setting (`stretches` on box panels, `sizes` on split
panels, `areas` on grid panels) attached to the child it was given for, through every change to
the child list: add, remove, move, reorder by assignment, and a tab or pane drag in the browser.

#### Scenario: Move keeps the stretch with its child

- **WHEN** a box panel has children `a` and `b` with `stretches=[1, 3]` and `a` is moved to
  index 1
- **THEN** `child_keys` is `["b", "a"]` and `stretches` is `[3, 1]`

#### Scenario: Reassignment reorders split sizes

- **WHEN** a split panel has children `a` and `b` with `sizes=[1, 3]` and `widgets` is assigned
  `[b, a]`
- **THEN** `sizes` is `[3, 1]`

#### Scenario: Reassignment drops a removed child's grid area

- **WHEN** a grid panel has children `a` and `b` with an area set for `a` only, and `widgets` is
  assigned `[b]`
- **THEN** `areas` holds one entry, the empty area that belonged to `b`

#### Scenario: Added child gets a neutral setting

- **WHEN** a child is added to a panel whose per-child setting list is not empty
- **THEN** the list grows by one neutral entry (stretch `0`, an equal share of split size, or an
  empty area), so its length equals the number of children

#### Scenario: Empty setting list stays empty

- **WHEN** a child is added, moved, or removed on a panel whose per-child setting list is empty
- **THEN** the list stays empty

### Requirement: Scrolling box spacing

A box panel with scrolling enabled SHALL separate its children by `spacing` pixels, as a box panel
without scrolling does.

#### Scenario: Custom spacing in a scroll box

- **WHEN** `BoxPanel(children, scroll=True, spacing=20)` is displayed
- **THEN** adjacent children are 20 pixels apart

### Requirement: Action separators

A toolbar action or menu item with a truthy `separator` key SHALL render as a visual separator
and SHALL NOT be activatable. A menu item with `type` equal to `"separator"` SHALL keep working.

#### Scenario: Toolbar separator

- **WHEN** a toolbar is built from `[{"id": "run", "label": "Run"}, {"separator": True},
  {"id": "stop", "label": "Stop"}]`
- **THEN** it shows two buttons with a separator between them, and no empty button

#### Scenario: Menu separator

- **WHEN** a menu's `items` contain `{"separator": True}` between two items
- **THEN** the menu shows a separator line there, and no blank menu entry

### Requirement: Command icons belong to their widget

An icon declared on an action SHALL appear only on that action in the widget that declares it.

#### Scenario: Two menus share an action id

- **WHEN** two menu bars on one page each declare an action with id `open` and different icons
- **THEN** each menu shows its own icon for `open`

### Requirement: Bundle load failure is visible

When a widget's frontend bundle does not arrive within a bounded time, each affected widget SHALL
show a message that names the failure, and a later widget on the same page SHALL retry the load.

#### Scenario: Kernel does not answer the bundle request

- **WHEN** a widget is rendered and its kernel never answers the bundle request
- **THEN** the widget shows a load failure message instead of staying blank

#### Scenario: Retry after a failed load

- **WHEN** a bundle load failed and a new widget is displayed from a live kernel
- **THEN** the new widget requests the bundle again and renders

### Requirement: Supported anywidget versions import cleanly

The package SHALL import on every anywidget version its dependency range allows, and SHALL raise
an error that names the incompatible version when it cannot resolve a widget's model id.

#### Scenario: Lookup function is missing

- **WHEN** the installed anywidget does not provide the model id lookup the package relies on
- **THEN** `import anylumino` raises an `ImportError` that names anywidget and its version
