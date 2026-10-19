# Table

A table of row objects; columns lists the keys to show.

In Python: `ax.Table(rows=..., columns=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `row_key` | `string` | Row id field. Use `None` to generate notebook-local row ids. |
| `selected` | `any[]` | Initially selected row ids. |
| `selects` | `"" \| "single" \| "multiple"` | Selection mode. Use `""` for no checkbox column. |
| `sortable` | `boolean` | Whether table columns should be sortable by default. |
| `sort_key` | `string` | Initially sorted table column key. |
| `sort_direction` | `"" \| "asc" \| "desc"` | Initial sort direction. Use `""` for unsorted. |
| `select_all_label` | `string` | Accessible label for the select-all checkbox. |
| `width` | `number \| string` | CSS width. Numbers are normalized by anylumino where supported. |
| `height` | `number \| string` | CSS height. Numbers are normalized by anylumino where supported. |
| `density` | `"compact" \| "balanced" \| "spacious"` | Compact, balanced, or spacious row density. |
| `dividers` | `"rows" \| "columns" \| "grid" \| "none"` | Row, column, grid, or no divider treatment. |
| `striped` | `boolean` | Whether alternating rows receive a background wash. |
| `hover` | `boolean` | Whether rows highlight on pointer hover. |
| `vertical_align` | `"middle" \| "top" \| "bottom"` | Body-cell vertical alignment. |
| `text_overflow` | `"wrap" \| "truncate"` | Wrap or truncate overflowing cell text. |
