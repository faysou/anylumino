---
name: openui-components
description: Options and Python constructors of the anylumino OpenUI components. Use before you pass an options object to a component in an openui-lang program, or build a component's widget in Python.
---

# OpenUI component options

Most components below take an optional `options` object as their last argument. Its keys are extra
keyword options of the anylumino widget, for example:

```openui-lang
table = Table(rows, ["region", "revenue"], {sortable: true, density: "compact"})
```

Read the component's file before you use its options. Each file lists the option names, types,
and meanings. Option values must be literals. An unknown option or a value of the wrong type stops
the workbench from applying the reply.

Each file also gives the Python constructor that builds the component's widget, for callbacks that
fill a container in Python. Pass the arguments by keyword: the Python positional order differs from
the OpenUI one.

| Component | File |
| --------- | ---- |
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
| `Badge` | [components/Badge.md](components/Badge.md) |
| `Table` | [components/Table.md](components/Table.md) |
| `CodeBlock` | [components/CodeBlock.md](components/CodeBlock.md) |
| `Plot` | [components/Plot.md](components/Plot.md) |
