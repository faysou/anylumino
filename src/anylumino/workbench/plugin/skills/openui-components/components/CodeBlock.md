# CodeBlock

Highlighted source code.

In Python: `ax.CodeBlock(code=..., language=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `title` | `string` | Header filename or label. |
| `language_label` | `boolean` | Whether to show the language in the header. |
| `line_numbers` | `boolean` | Whether to show the line-number gutter. |
| `highlight_lines` | `number[]` | One-indexed lines to highlight. |
| `copy_button` | `boolean` | Whether to show the copy control. |
| `wrapped` | `boolean` | Whether long lines wrap instead of scrolling. |
| `max_height` | `number \| string` | Maximum height before vertical scrolling. |
| `size` | `"sm" \| "md"` | Code text size. |
| `width` | `string` | CSS width of the code block. |
| `container` | `"card" \| "section"` | Card or section presentation. |
| `collapsible` | `boolean` | Whether long code can collapse. |
| `collapsible_threshold` | `number` | Minimum line count for the collapse control. |
