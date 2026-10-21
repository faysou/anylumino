# Toast

Notifications that callbacks show with self.ui.<name>.notify(text).

In Python: `ax.Toast()`, plus any option below as a keyword.

## Options

| Option | Type | Meaning |
| ------ | ---- | ------- |
| `position` | `"topEnd" \| "topStart" \| "bottomEnd" \| "bottomStart"` | Window corner the toasts stack in. |
| `max_visible` | `number` | Most toasts shown at once; older ones queue. |
