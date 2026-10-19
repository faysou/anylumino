# HBox

Places children left to right at their natural size; gap is an Astryx spacing step.

In Python: `ax.Stack(children=..., gap=..., direction='horizontal')`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `align` | `"start" \| "center" \| "end" \| "stretch"` | Cross-axis alignment. |
| `justify` | `"start" \| "center" \| "end" \| "between" \| "around" \| "evenly"` | Main-axis alignment. |
| `width` | `number \| string` | Container width. |
| `height` | `number \| string` | Container height. |
| `padding` | `number` | Inner padding using the Astryx spacing scale. |
| `wrap` | `"nowrap" \| "wrap" \| "wrap-reverse"` | Stack wrapping behavior. |
| `scrollable` | `boolean` | Whether overflow should scroll. |
