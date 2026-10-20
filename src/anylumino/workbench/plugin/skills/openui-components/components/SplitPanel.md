# SplitPanel

Resizable panes; sizes are relative weights.

In Python: `al.SplitPanel(widgets=..., orientation=..., sizes=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `titles` | `string[] \| object` | Optional labels associated with children. |
| `keys` | `string[]` | Stable child keys for iterable `widgets`. |
| `spacing` | `number` | Pixel spacing around Lumino split handles. |
| `width` | `number \| string` | Widget width. |
| `height` | `number \| string` | Widget height. |
| `resizable` | `boolean` | Whether the whole panel gets a notebook resize handle. Lumino pane dividers remain draggable independently. |
| `fit_content` | `boolean` | Whether the panel height follows its panes' content instead of `height`: the tallest pane side by side, or the panes and handles stacked. The panel refits when a pane's content changes size, such as a chart frame that grows with its subcharts. |
