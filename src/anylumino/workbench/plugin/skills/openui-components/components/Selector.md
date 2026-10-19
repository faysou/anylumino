# Selector

A dropdown of string items; on_change runs with the chosen item.

In Python: `ax.Selector(items=..., value=..., label=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `label_position` | `"top" \| "left"` | Place the label above the control or beside it in a compact row. |
| `label_width` | `number \| string` | Width of a left-side label. Use the same width to align sibling controls. |
| `disabled` | `boolean` | Whether the selector is disabled. |
| `placeholder` | `string` | Placeholder shown when no option is selected. |
| `size` | `"sm" \| "md" \| "lg"` | Selector size. |
| `clear` | `boolean` | Whether to show a clear button. |
| `search` | `boolean` | Whether to show option filtering. |
| `search_placeholder` | `string` | Placeholder for the search input. |
| `label_hidden` | `boolean` | Whether to visually hide the accessible label. |
| `description` | `string` | Helper text displayed with the selector. |
| `status` | `object` | Validation status record. |
