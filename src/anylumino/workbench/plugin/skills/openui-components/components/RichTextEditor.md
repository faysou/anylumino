# RichTextEditor

A rich text editor; on_change runs with the new Markdown.

In Python: `ax.RichTextEditor(label=..., value=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `placeholder` | `string` | Placeholder text shown when the editor is empty. |
| `disabled` | `boolean` | Whether the component should render disabled. |
| `read_only` | `boolean` | Whether the content can be selected but not edited. |
| `toolbar` | `boolean` | Whether to show the formatting toolbar. |
| `size` | `"sm" \| "md" \| "lg"` | Editor size. |
| `label_hidden` | `boolean` | Whether to visually hide the accessible label. |
| `description` | `string` | Helper text displayed with the editor. |
| `optional` | `boolean` | Whether to mark the field optional. |
| `required` | `boolean` | Whether to mark the field required. |
| `min_height` | `number \| string` | Minimum height of the editable surface. |
| `max_length` | `number` | Maximum length shown by the character counter. Astryx does not enforce it. |
| `status` | `object` | Validation status record. |
