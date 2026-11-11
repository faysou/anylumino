## ADDED Requirements

### Requirement: Tabulator catalog component

The catalog SHALL include a `Tabulator` component that builds `al.Tabulator`, with props `data`
(an array of row objects) and `columns` (an array of Tabulator column definitions) and the options
its constructor accepts.

#### Scenario: Program places a grid

- **WHEN** a program contains `grid = Tabulator([{id: 1, symbol: "ESZ6"}], [{title: "Symbol", field: "symbol"}])`
- **THEN** the generated Python creates `self.grid = al.Tabulator(data=[...], columns=[...])` and
  the workbench shows the grid

#### Scenario: Callback sends a delta

- **WHEN** a callback of the program calls `self.ui.grid.update_rows([{"id": 1, "symbol": "NQZ6"}])`
- **THEN** the displayed grid shows `NQZ6` in that row

### Requirement: JavaScript functions in Tabulator programs

A program MAY give a JavaScript function anywhere in the `columns` or `options` of a `Tabulator`
component as an object with the single key `$js` and the function source as its value. The
generated Python SHALL pass that object through unchanged. The component's skill page SHALL
document the `$js` form and state that the source runs in the page.

#### Scenario: Program uses a JavaScript formatter

- **WHEN** a program column sets `formatter: {"$js": "function(cell) { return cell.getValue(); }"}`
- **THEN** generation succeeds and the generated column definition holds the same `$js` mapping

#### Scenario: Skill page documents the form

- **WHEN** the component skill is generated
- **THEN** the `Tabulator` page shows a `$js` example and states that its source runs in the page
