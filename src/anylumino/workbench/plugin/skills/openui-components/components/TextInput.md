# TextInput options

A single-line text field; on_change runs with the new text.

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `label_position` | `"top" \| "left"` | Place the label above the control or beside it in a compact row. |
| `label_width` | `number \| string` | Width of a left-side label. Use the same width to align sibling controls. |
| `disabled` | `boolean` | Whether the component should render disabled. |
| `input_type` | `"text" \| "password" \| "email"` | HTML text input type. |
| `size` | `"sm" \| "md" \| "lg"` | Input size. |
| `label_hidden` | `boolean` | Whether to visually hide the accessible label. |
| `description` | `string` | Helper text displayed with the input. |
| `optional` | `boolean` | Whether to mark the field optional. |
| `required` | `boolean` | Whether to mark the field required. |
| `loading` | `boolean` | Whether to show the loading state. |
| `status` | `object` | Validation status record. |
| `clear` | `boolean` | Whether to show a clear button. |
| `auto_focus` | `boolean` | Whether to focus the input when mounted. |
| `select_on_focus` | `boolean` | Whether focusing the input selects its content, so typing replaces the value. Off by default for text inputs. |
