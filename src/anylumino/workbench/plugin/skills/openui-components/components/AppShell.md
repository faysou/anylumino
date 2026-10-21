# AppShell

An app frame around content, with a TopNav in top_nav and a SideNav in side_nav.

In Python: `ax.AppShell(content=..., top_nav=..., side_nav=..., banner=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `variant` | `"wash" \| "surface" \| "section" \| "elevated"` | Surface treatment of the content area. |
| `content_padding` | `number` | Padding around the content using the Astryx spacing scale. |
| `height` | `"fill" \| "auto"` | Whether the shell fills its container or fits its content. |
