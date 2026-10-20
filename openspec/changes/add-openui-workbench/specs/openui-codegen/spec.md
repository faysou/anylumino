# Spec Delta

## Purpose

Turns OpenUI Lang programs written by an agent into Python that builds anylumino widgets, using a
component catalog that also produces the OpenUI library spec and the agent system prompt.

## ADDED Requirements

### Requirement: Component catalog

The system SHALL define one catalog of the anylumino and Astryx components that an OpenUI program
may use. Each entry SHALL name the component, describe it, and list its props in positional order
with types and required flags. The catalog SHALL cover at least: split, tab, horizontal, and
vertical layout panels; Card; Heading; Text; Markdown; Button; TextInput; TextArea; NumberInput;
Selector; Slider; Switch; Checkbox; Badge; Table; CodeBlock; a Plotly figure, when Plotly is
installed; and a component that mounts a widget from the workbench namespace by name. The OpenUI library spec SHALL be derived from this catalog,
not written separately.

#### Scenario: Library spec matches the catalog

- **WHEN** the library spec is produced from the catalog
- **THEN** it lists every catalog component with the catalog's props in the same order, and no
  other components

### Requirement: Component options

Every catalog component whose widget has keyword options that the positional props do not cover
SHALL end with an optional `options` object prop. Its keys SHALL be derived from the widget's
constructor keywords, with JSON Schema types from the annotations and descriptions from the
docstring. Keywords whose types have no OpenUI literal, such as callables, SHALL be left out. The
parser SHALL type-check option values, and code generation SHALL pass each option as a keyword
and reject an option the component does not have, naming the statement.

#### Scenario: Table options reach the widget

- **WHEN** a program contains `t = Table(rows, ["a"], {sortable: true})`
- **THEN** the generated code builds `ax.Table(..., sortable=True)`

#### Scenario: Unknown option is rejected

- **WHEN** a program passes `{sorted: true}` to `Table`
- **THEN** generation fails with `t.options: Table has no option 'sorted'`

### Requirement: Component options skill

The system SHALL generate one agent skill from the catalog that documents each component's options
with their names, types, and descriptions, one file per component. The skill SHALL live in a
Claude Code plugin directory inside the package, and a test SHALL fail when the files differ from
the catalog. The system prompt SHALL list only the component signatures and SHALL point the agent
to the skill and its file path before it uses options.

#### Scenario: Skill files are current

- **WHEN** the catalog or a widget's keywords change and the skill is not regenerated
- **THEN** the skill test fails

#### Scenario: Prompt stays short

- **WHEN** the system prompt is generated
- **THEN** it names the skill and its path, and does not list the individual options

### Requirement: Generated system prompt

The system SHALL generate the agent system prompt from the library spec with the OpenUI prompt
generator, with inline mode and edit mode on, and with tools, queries, mutations, and `$state`
bindings off. The prompt SHALL also teach the `@Callback(handler, context?)` action, the `App`
subclass that holds the handlers as methods, and that the callbacks are returned in one fenced
`python` block.

#### Scenario: Prompt teaches only supported features

- **WHEN** the system prompt is generated
- **THEN** it documents every catalog component and `@Callback`, and does not teach `Query`,
  `Mutation`, `@Run`, or `$variables`

### Requirement: Parsing and merging programs

The system SHALL parse an OpenUI Lang program against the library spec, and return the component
tree with each component's statement name, type, and named props, plus the parse errors. When a
current program exists, the system SHALL merge a new program into it by statement name, following
OpenUI incremental editing, before parsing.

#### Scenario: Valid program

- **WHEN** the program `root = VBox([title, go])`, `title = Heading("Sales")`,
  `go = Button("Run", @Callback("on_run"))` is parsed
- **THEN** the tree root is a `VBox` named `root` with children `title` (Heading, text `Sales`)
  and `go` (Button, label `Run`, action `Callback` with handler `on_run`), and there are no errors

#### Scenario: Patch merge

- **WHEN** the current program contains `title = Heading("Sales")` and the patch is
  `title = Heading("Revenue")`
- **THEN** the merged program keeps every other statement and `title` has text `Revenue`

#### Scenario: Unknown component

- **WHEN** a program uses a component that is not in the catalog
- **THEN** parsing reports an error that names that component

### Requirement: Python code generation

The system SHALL generate, from a parsed tree, a Python module that imports anylumino and defines
a `UI` class that subclasses `anylumino.workbench.View`. `UI(app)` SHALL create each widget with its catalog constructor (namespace
components take the `app` attribute of their name), store each named widget as an attribute named
after its statement, bind the actions to `app` with an `Event` per activation, keep the root widget as `widget`, and call
`app.set_ui`. Statement names SHALL NOT be `app` or `widget`. The same tree SHALL
always produce the same source text. Generation SHALL fail with an error that names the statement
when a prop holds a dynamic expression, when a referenced namespace widget is missing, or when an
`@Callback` handler is not a method of the `App` subclass.

#### Scenario: Deterministic output

- **WHEN** the same program is generated twice
- **THEN** both source texts are identical

#### Scenario: Generated module runs on its own

- **WHEN** the exported module is imported in a new kernel, and `UI(app)` is called with an `App`
  subclass created with the namespace
- **THEN** a cell shows the UI's root `widget`, `app.ui` is that UI, and it has an attribute for every
  named statement

#### Scenario: Missing handler

- **WHEN** a program uses `@Callback("on_run")` and the `App` subclass has no `on_run` method
- **THEN** generation fails with an error naming `on_run` and the statement that uses it

### Requirement: Callback binding

Generated code SHALL connect each `@Callback(handler, context)` action to the widget event that
the catalog assigns to that prop (activation for buttons, value change for inputs). It SHALL call
the app's `handler(event)` method through `app.call`, where `event` holds the source statement
name, the new value or `None`, and the action context. Generated code SHALL connect an
`@ToAssistant(message, context)` action to `app.ask_agent` with the message and context.

#### Scenario: Button click runs its handler

- **WHEN** the user activates a Button that was generated from `@Callback("on_run", "q3")`
- **THEN** the app's `on_run` method receives an event with source `go`, value `None`, and
  context `q3`

#### Scenario: Input change runs its handler

- **WHEN** the value of a TextInput generated with an `@Callback("on_region")` change action
  becomes `EMEA`
- **THEN** `on_region` receives an event with that input's name and value `EMEA`

#### Scenario: Ask the assistant from the UI

- **WHEN** the user activates a Button generated from `@ToAssistant("Explain this chart")`
- **THEN** `app.ask_agent` is called with `Explain this chart`

### Requirement: App controller

`anylumino.workbench.App` SHALL be a plain class that holds the data and handlers of one UI.
`App(**namespace)` SHALL store each namespace entry as an attribute and
SHALL reject a name that is not an identifier or that an `App` attribute or method already uses.
`app.set_ui(ui)` SHALL keep `ui` as `app.ui` and run `setup`, and SHALL raise `RuntimeError` when
the app already drives another UI. `app.call(handler, event)` SHALL run the handler method, and SHALL pass an exception to
`app.on_error` when one is set. `app.ask_agent(message, context)` SHALL call `app.agent` when one
is set, and SHALL warn and do nothing otherwise. A callbacks module SHALL define exactly one `App`
subclass, and its methods SHALL NOT replace an `App` attribute other than `setup`.

#### Scenario: App in another layout

- **WHEN** `UI(SalesApp(sales=sales))` is a tab of an `al.TabPanel`
- **THEN** the tab shows the UI's root widget, and its handlers read `self.sales`

#### Scenario: Handler shadows a widget member

- **WHEN** the `App` subclass defines a method `call`
- **THEN** the callbacks are rejected with an error that names `call`
