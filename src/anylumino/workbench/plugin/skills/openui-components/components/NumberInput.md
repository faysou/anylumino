# NumberInput

A number field; on_change runs with the new number.

In Python: `ax.NumberInput(label=..., value=..., min=..., max=..., step=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `label_hidden` | `boolean` | Whether to visually hide the accessible label. |
| `disabled` | `boolean` | Whether the component should render disabled. |
| `units` | `string` | Units displayed after the value. |
| `size` | `"sm" \| "md" \| "lg"` | Input size. |
| `placeholder` | `string` | Placeholder text. |
| `integer_only` | `boolean` | Whether to accept only integer values. |
| `clear` | `boolean` | Whether to show a clear button. |
| `description` | `string` | Helper text displayed with the input. |
| `status` | `object` | Validation status record. |
| `select_on_focus` | `boolean` | Whether focusing the input selects its content, so typing replaces the value. On by default for numeric inputs; pass `False` to opt out. |
