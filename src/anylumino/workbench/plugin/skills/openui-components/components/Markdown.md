# Markdown

Rendered Markdown text.

In Python: `ax.Markdown(text=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `display` | `"block" \| "inline"` | Block or inline display. |
| `density` | `"default" \| "compact"` | Default or compact block spacing. |
| `heading_level_start` | `number` | Heading level corresponding to Markdown `#`. |
| `streaming` | `boolean` | Whether to use incremental streaming presentation. |
| `sources` | `object` | Citation sources keyed by identifier. |
| `citation_style` | `"label" \| "number"` | Label or numeric citations. |
| `content_width` | `number \| string` | Maximum prose width. |
| `content_align` | `"start" \| "center"` | Prose alignment inside the available width. |
| `autolink` | `"gfm"` | Optional GFM bare-link handling. |
