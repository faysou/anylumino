# Layout

Content with header, footer, and start and end side panels.

In Python: `ax.Layout(content=..., header=..., start=..., end=..., footer=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `start_width` | `number \| string` | Width of the start panel. |
| `end_width` | `number \| string` | Width of the end panel. |
| `dividers` | `boolean` | Whether borders separate the regions. |
| `content_width` | `number \| string` | Maximum width of the content in each region. |
| `height` | `"fill" \| "auto"` | Whether the layout fills its container or fits its content. |
| `padding` | `number` | Padding of each region using the Astryx spacing scale. |
