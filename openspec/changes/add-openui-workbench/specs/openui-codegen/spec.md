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
Selector; Slider; Switch; Checkbox; Badge; Table; CodeBlock; and a component that mounts a widget
from the workbench namespace by name. The OpenUI library spec SHALL be derived from this catalog,
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
bindings off. The prompt SHALL also teach the `@Callback(handler, context?)` action, the callback
function signature, and that callbacks are returned in one fenced `python` block.

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

The system SHALL generate, from a parsed tree, a Python module that imports anylumino, defines
`build(callbacks, namespace=None, ask_agent=None)`, creates each widget with its catalog constructor
(namespace components take the widget stored under their name), and registers each named widget
under its statement name in a `widgets` dict. `build` SHALL return the root
widget and `widgets`. The same tree SHALL always produce the same source text. Generation SHALL fail
with an error that names the statement when a prop holds a dynamic expression, when a referenced
namespace widget is missing, or when an `@Callback` handler is not defined in the callbacks.

#### Scenario: Deterministic output

- **WHEN** the same program is generated twice
- **THEN** both source texts are identical

#### Scenario: Generated module runs on its own

- **WHEN** the generated module and its callbacks module are loaded in a new kernel and `build` is
  called with the callbacks and the namespace
- **THEN** it returns a root widget, and `widgets` holds an entry for every named statement

#### Scenario: Missing handler

- **WHEN** a program uses `@Callback("on_run")` and the callbacks define no `on_run`
- **THEN** generation fails with an error naming `on_run` and the statement that uses it

### Requirement: Callback binding

Generated code SHALL connect each `@Callback(handler, context)` action to the widget event that
the catalog assigns to that prop (activation for buttons, value change for inputs). It SHALL call
`handler(event, widgets)`, where `event` holds the source statement name, the new value or `None`,
and the action context. Generated code SHALL connect an `@ToAssistant(message, context)` action
to `ask_agent` with the message and context.

#### Scenario: Button click runs its handler

- **WHEN** the user activates a Button that was generated from `@Callback("on_run", "q3")`
- **THEN** `on_run` receives an event with source `go`, value `None`, and context `q3`, plus the
  widgets dict

#### Scenario: Input change runs its handler

- **WHEN** the value of a TextInput generated with an `@Callback("on_region")` change action
  becomes `EMEA`
- **THEN** `on_region` receives an event with that input's name and value `EMEA`

#### Scenario: Ask the assistant from the UI

- **WHEN** the user activates a Button generated from `@ToAssistant("Explain this chart")`
- **THEN** `ask_agent` is called with `Explain this chart`
