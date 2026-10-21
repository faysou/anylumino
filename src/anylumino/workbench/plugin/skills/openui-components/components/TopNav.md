# TopNav

Top navigation of labels or {label, value, icon, items} records, where items opens a dropdown; on_change runs with the selected or clicked value.

In Python: `ax.TopNav(items=..., value=..., end=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `heading` | `string` | Title shown at the start of the bar. |
| `subheading` | `string` | Text shown under the heading. |
| `icon` | `string` | Astryx icon name shown as the logo. |
| `menu` | `any[]` | Heading menu entries as labels or records with `label` and optional `value`, `description`, and `disabled` keys. A click sends the entry value as an action. |
| `label` | `string` | Accessible label of the navigation. |
