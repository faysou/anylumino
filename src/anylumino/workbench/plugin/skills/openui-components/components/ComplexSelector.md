# ComplexSelector

A selector whose popup holds content; a callback sets self.ui.<name>.value and calls .hide().

In Python: `ax.ComplexSelector(label=..., content=..., value=...)`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `label_hidden` | `boolean` | Whether to visually hide the accessible label. |
| `trigger_label` | `string` | Text shown on the trigger instead of `value`. |
| `placeholder` | `string` | Trigger text shown while `value` is empty. |
| `description` | `string` | Helper text displayed with the selector. |
| `size` | `"sm" \| "md" \| "lg"` | Trigger size. |
| `variant` | `"input" \| "secondary" \| "ghost"` | Input, secondary, or ghost trigger style. |
| `width` | `number \| string` | Trigger width. |
| `disabled` | `boolean` | Whether the selector is disabled. |
