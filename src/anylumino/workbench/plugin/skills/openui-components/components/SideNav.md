# SideNav

Side navigation of labels or {label, value, icon, items} records; {type: "section", title, items} groups them; on_change runs with the selected value.

In Python: `ax.SideNav(items=..., value=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `heading` | `string` | Title shown above the items. |
| `subheading` | `string` | Text shown under the heading. |
| `icon` | `string` | Astryx icon name shown beside the heading. |
| `menu` | `any[]` | Heading menu entries as labels or records with `label` and optional `value`, `description`, and `disabled` keys. A click sends the entry value as an action. |
| `collapsible` | `boolean` | Whether a button collapses the navigation to icons. |
| `resizable` | `boolean` | Whether the navigation width can be dragged. |
