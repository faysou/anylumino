# TabPanel options

One tab per child, titled in order.

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `keys` | `string[]` | Stable child keys for iterable `widgets`. Do not pass this when `widgets` is a mapping. |
| `selected_index` | `number` | Initially selected tab index. |
| `tab_placement` | `"top" \| "bottom" \| "left" \| "right"` | Where Lumino should place the tab bar. |
| `tabs_movable` | `boolean` | Whether tabs can be reordered in the frontend. A drag reorders `widgets`, `child_keys`, and `titles` in Python too, so `selected_key` keeps naming the visible child. |
| `width` | `number \| string` | Widget width. Numbers above 1 are pixels, numbers between 0 and 1 are percentages, and strings are passed through as CSS sizes. |
| `height` | `number \| string` | Widget height. Numbers above 1 are pixels, numbers between 0 and 1 are percentages, and strings are passed through as CSS sizes. |
| `resizable` | `boolean` | Whether the panel receives a notebook-friendly resize handle. |
| `fit_content` | `boolean` | Whether the panel height follows the tab bar and the selected tab's content, with a 180 pixel minimum, instead of `height`. |
