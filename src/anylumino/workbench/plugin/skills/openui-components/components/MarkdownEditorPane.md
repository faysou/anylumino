# MarkdownEditorPane

A Markdown source editor beside its rendered view, math and Mermaid diagrams included, with a draggable split; on_change runs with the new Markdown once typing pauses.

In Python: `ax.MarkdownEditorPane(value=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `width` | `number \| string` | CSS width. Numbers are normalized by anylumino where supported. |
| `height` | `number \| string` | CSS height. Both panes scroll inside this height, so it needs a definite value. Numbers are normalized by anylumino where supported. |
