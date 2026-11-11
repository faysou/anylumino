# Tabulator

A virtualized data grid of row objects with Tabulator column definitions, such as {title: "Last", field: "last", editor: "number"}; a callback changes rows with self.ui.grid.update_rows, add_rows, upsert_rows, or delete_rows. Wherever Tabulator takes a function, pass {"$js": "function(cell) { return cell.getValue(); }"}: its JavaScript source runs in the page.

In Python: `al.Tabulator(data=..., columns=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `index` | `string` | Row id field. When no row has it, rows get the ids `0, 1, 2, ...`. |
| `options` | `object` | Other Tabulator constructor options, such as `layout` or `selectableRows`. `data`, `columns`, and `index` have their own arguments. |
| `selected` | `any[]` | Index values of the initially selected rows. |
| `transport` | `"auto" \| "json" \| "arrow"` | How rows reach the browser. `"auto"` sends Arrow IPC for columnar input when `pyarrow` imports, and JSON otherwise. |
| `width` | `number \| string` | CSS width; `"100%"` when omitted. Inside a layout panel the grid fills its slot instead, as for `height`. |
| `height` | `number \| string` | CSS height; `"320px"` when omitted. The grid needs a bounded height to render only its visible rows. Inside a layout panel the grid fills its slot instead, except in a scroll box or a `fit_content` panel. |
