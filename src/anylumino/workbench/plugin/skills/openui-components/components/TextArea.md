# TextArea

A multi-line text field; on_change runs with the new text.

In Python: `ax.TextArea(label=..., value=..., placeholder=..., rows=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `disabled` | `boolean` | Whether the component should render disabled. |
| `size` | `"sm" \| "md" \| "lg"` | Text-area size. |
| `label_hidden` | `boolean` | Whether to visually hide the accessible label. |
| `description` | `string` | Helper text displayed with the input. |
| `optional` | `boolean` | Whether to mark the field optional. |
| `required` | `boolean` | Whether to mark the field required. |
| `loading` | `boolean` | Whether to show the loading state. |
| `max_length` | `number` | Maximum length used by the character counter. |
| `spell_check` | `boolean` | Whether browser spell checking is enabled. |
| `status` | `object` | Validation status record. |
