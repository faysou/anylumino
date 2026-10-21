# OverflowList

Buttons that overflow into a More menu; action runs with the clicked item.

In Python: `ax.OverflowList(items=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `label` | `string` | Accessible label of the menu button that holds the hidden items. |
| `gap` | `number` | Astryx spacing step between buttons. |
| `min_visible` | `number` | Fewest buttons kept visible. |
| `max_visible` | `number` | Most buttons shown before the rest collapse. |
| `collapse_from` | `"start" \| "end"` | Which end collapses first. |
| `size` | `"sm" \| "md" \| "lg"` | Button size. |
