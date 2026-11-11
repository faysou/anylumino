# OpenUI in the workbench

The workbench turns an agent's reply into a notebook UI in three steps: it parses
an [OpenUI Lang](https://github.com/thesysdev/openui) program, generates a Python
module with a `UI` class from the parsed tree, and builds that class with the
reply's callbacks. This note describes those three steps. For using the
workbench, sessions, export, and the full turn, see
[the workbench guide](../content/docs/workbench.mdx).

## The program

A reply carries one `openui-lang` fence and one `python` fence. The program
names one component per statement, and `root` is the top of the tree:

```text
root = VBox([title, total])
title = Heading("Sales")
total = Button("Total", @Callback("on_total"))
```

The components, their props, and their option values come from the catalog in
`src/anylumino/workbench/catalog.py`. Option values follow each widget
constructor's annotations: an enum or a `Literal` type lists the values the
agent may use.

## Parsing

`openui.parse` runs the official `@openuidev/lang-core` parser under Node and
returns a `ParseResult`: the evaluated tree in `root`, the parser `errors`, the
`unresolved` names, and the statement names. The workbench applies a program
only when it has no errors, is complete, and defines every name it uses. A
rejected program leaves the UI unchanged, and the error names each statement:

```text
OpenUI errors: root: `chart` is not defined
```

A follow-up turn can send only the statements that change. `openui.merge`
merges them into the current program by statement name, as OpenUI edit mode
does.

## The generated `UI` class

`codegen.generate` turns a parse result into a module with one class, `UI`.
Each statement becomes an attribute of the same name, and children are created
before their parents. This example generates the module for the program above:

```python
import asyncio

from anylumino.workbench import codegen, openui

program = (
    "root = VBox([title, total])\n"
    'title = Heading("Sales")\n'
    'total = Button("Total", @Callback("on_total"))'
)
result = asyncio.run(openui.parse(program))
source = codegen.generate(result, {"on_total"}, {})

assert "class UI(View):" in source
assert "self.total = ax.Button(" in source
```

`UI` is a `View`, not a widget: it shows through its root `widget`, so every
statement name except `app` and `widget` is free for the program to use.

## Callbacks

The `python` fence defines an `App` subclass. Its methods are the handlers that
`@Callback("name")` binds, and `self.ui` is the generated view:

```python
from anylumino.workbench import App


class SalesApp(App):
    def on_total(self, event):
        self.ui.title.text = "Total 3.5"
```

The workbench builds `UI(app)` with an instance of that class. The namespace
reaches the app through its constructor, so an exported module runs with the
same explicit inputs outside the workbench.
