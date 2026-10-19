# Spec Delta

## Purpose

A notebook workbench that pairs an agent chat with a live, generated anylumino UI, and shows the
OpenUI program, generated UI code, and callbacks behind it, with named sessions that survive
kernel restarts.

## ADDED Requirements

### Requirement: Workbench layout

The workbench SHALL be one displayable widget: a horizontal split with the chat on the left and a
tab panel on the right. The tab panel SHALL hold, in order, the tabs `UI`, `OpenUI`, `UI code`,
and `Callbacks`. The chat side SHALL show the agent, the session name, and the turn status.

#### Scenario: Fresh workbench

- **WHEN** a workbench is created with no saved session and displayed
- **THEN** the chat is on the left, the four tabs are on the right with `UI` selected, and the
  `UI` tab shows an empty state

### Requirement: Read-only code tabs

The `OpenUI`, `UI code`, and `Callbacks` tabs SHALL show their text with syntax highlighting,
and SHALL NOT accept edits. Only chat turns SHALL change them.

#### Scenario: Code tab cannot be edited

- **WHEN** the user opens the `Callbacks` tab and types into it
- **THEN** the text does not change

### Requirement: Applying a turn

After a turn ends, the workbench SHALL merge and parse the program, generate the UI code, and run
the callbacks and the UI code to build the live UI. All of these SHALL succeed before any tab
changes. Then all four tabs SHALL update together. On any failure, the workbench SHALL keep the
previous program, UI code, callbacks, and live UI, and SHALL show the error in the chat as a system
message. A failure of the agent itself, including output it cannot read, SHALL end the turn with
a system message and leave the workbench ready for the next turn. A new live UI SHALL close the
widgets of the previous one, except widgets from the namespace. A program without callbacks SHALL
get an empty `App` subclass.

#### Scenario: Successful turn

- **WHEN** a turn returns a valid program and callbacks
- **THEN** the `UI` tab shows the new widgets, and the three code tabs show the merged program,
  the generated code, and the callbacks from that turn

#### Scenario: Failing callbacks keep the old state

- **WHEN** a turn returns callbacks with a syntax error
- **THEN** the four tabs keep their previous contents, and the chat shows a system message with the
  error and its line

#### Scenario: Unreadable agent output

- **WHEN** the agent CLI writes a line that is not JSON
- **THEN** the chat shows a system message with the error, and the status returns to `Ready`

#### Scenario: Live UI runs the shown code

- **WHEN** a turn has been applied
- **THEN** the live UI is the result of running exactly the text in the `UI code` tab

### Requirement: Namespace access

The workbench SHALL accept a namespace mapping when it is created. The callbacks SHALL run without notebook globals, and the
`App` subclass SHALL receive the namespace as constructor keywords. The system prompt context SHALL list each namespace
entry's name and type, plus the shape, column names, and column types of pandas and Polars data
frames. The namespace
component SHALL mount widgets from that namespace.

#### Scenario: Callback reads notebook data

- **WHEN** the namespace contains a data frame `sales` and a handler filters `self.sales`
- **THEN** activating the bound widget runs the filter on that data frame

### Requirement: Setup callback

When the `App` subclass defines `setup(self)`, it SHALL run once each time the UI is built,
after the widgets exist. The system prompt SHALL tell the agent to fill widgets from
namespace data there instead of copying the data into the program. An exception in `setup` SHALL
be reported in the chat and SHALL not stop the turn from applying.

#### Scenario: Setup fills a table from the namespace

- **WHEN** a turn applies callbacks whose `setup` calls `set_rows` with the rows of `sales`
- **THEN** the table in the `UI` tab shows those rows

### Requirement: Callback errors do not break the workbench

An exception raised by a callback SHALL be shown in the chat as a system message that names the
handler. The workbench and the other widgets SHALL keep working.

#### Scenario: Raising handler

- **WHEN** a handler raises `KeyError('region')`
- **THEN** the chat shows a system message naming the handler and the `KeyError`, and other
  buttons still run their handlers

### Requirement: Asking the agent from the UI

`app.ask_agent(message, context=None)` SHALL submit a chat turn with that message, as if the user had
typed it, with the context added to the prompt. While a turn is running, it SHALL be refused with
a system message.

#### Scenario: UI button starts a turn

- **WHEN** a generated button calls `app.ask_agent("Summarize the selection")` while no turn is running
- **THEN** a user message `Summarize the selection` appears and a turn starts

### Requirement: Named session persistence

A workbench created with a session name SHALL save, after each turn, a JSON file. The file SHALL
hold the session name, agent, agent session ID, working directory, messages, program, callbacks,
and update time. Creating a workbench with an existing session name SHALL restore the messages,
program, and callbacks, regenerate the UI code, rebuild the live UI, and resume the agent session.
Passing an agent that differs from the saved one SHALL raise `ValueError`.

#### Scenario: Restore after kernel restart

- **WHEN** a session `sales` has two applied turns, the kernel restarts, and
  `Workbench(session="sales")` is displayed
- **THEN** the chat shows the earlier messages, the four tabs match their state after the second
  turn, and the next turn resumes the same agent session

#### Scenario: Restore with an unrunnable UI

- **WHEN** a saved program references a namespace widget that is missing in the new kernel
- **THEN** the messages and code tabs are restored, the `UI` tab shows the error, and the chat
  stays usable

### Requirement: Export to files

The workbench header SHALL have an `Export` button, disabled until a UI is built. It SHALL open a
dialog that browses the kernel's folders, starting in the kernel's current directory, and asks for
a name. Exporting SHALL write one module `<name>.py` in the chosen folder, replacing an existing
file: the shown UI code first, then the shown callbacks, with the callbacks' leading imports moved
up to the UI code's imports. It SHALL post a chat message with the path and a `load` call that
uses it.

#### Scenario: Export a built UI

- **WHEN** a UI is built, the user opens `Export`, enters the folder `exports`, names the export
  `sales`, and confirms
- **THEN** `exports/sales.py` holds the `UI code` tab followed by the `Callbacks` tab, and the chat
  shows `load("exports/sales.py", sales=sales)`

### Requirement: Loading an exported file

`anylumino.workbench.load(path, **namespace)` SHALL run the file, create its `App` subclass with
`namespace`, and return a new `UI` built with that app. A relative path SHALL be relative to the
notebook's directory, or to the calling script's directory outside Jupyter. The exported file
SHALL read no notebook globals, so it also works as an imported module.

#### Scenario: Same UI outside the workbench

- **WHEN** a notebook runs `load("exports/sales.py", sales=sales)`
- **THEN** the returned UI is the same as the workbench's, `setup` has filled it from
  `sales`, and its handlers run against `sales`
