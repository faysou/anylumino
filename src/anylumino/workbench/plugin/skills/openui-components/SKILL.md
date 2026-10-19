---
name: openui-components
description: Options of the anylumino OpenUI components. Use before you pass an options object to a component in an openui-lang program.
---

# OpenUI component options

Each component below takes an optional `options` object as its last argument. Its keys are extra
keyword options of the anylumino widget, for example:

```openui-lang
table = Table(rows, ["region", "revenue"], {sortable: true, density: "compact"})
```

Read the component's file before you use its options. Each file lists the option names, types,
and meanings. Option values must be literals. An unknown option or a value of the wrong type stops
the workbench from applying the reply.

| Component | Options |
| --------- | ------- |
| `VBox` | [components/VBox.md](components/VBox.md) |
| `HBox` | [components/HBox.md](components/HBox.md) |
| `SplitPanel` | [components/SplitPanel.md](components/SplitPanel.md) |
| `TabPanel` | [components/TabPanel.md](components/TabPanel.md) |
| `Card` | [components/Card.md](components/Card.md) |
| `Heading` | [components/Heading.md](components/Heading.md) |
| `Text` | [components/Text.md](components/Text.md) |
| `Markdown` | [components/Markdown.md](components/Markdown.md) |
| `Button` | [components/Button.md](components/Button.md) |
| `TextInput` | [components/TextInput.md](components/TextInput.md) |
| `TextArea` | [components/TextArea.md](components/TextArea.md) |
| `NumberInput` | [components/NumberInput.md](components/NumberInput.md) |
| `Selector` | [components/Selector.md](components/Selector.md) |
| `Slider` | [components/Slider.md](components/Slider.md) |
| `Switch` | [components/Switch.md](components/Switch.md) |
| `Checkbox` | [components/Checkbox.md](components/Checkbox.md) |
| `Table` | [components/Table.md](components/Table.md) |
| `CodeBlock` | [components/CodeBlock.md](components/CodeBlock.md) |
