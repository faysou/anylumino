# Spec Delta

## Purpose

Turns an OpenUI Lang program into anylumino Python code, and builds the component catalog that
tells the agent which components, props, and option values it may use.

## ADDED Requirements

### Requirement: Unresolved references are rejected

A program that references a name it does not define SHALL NOT be applied. The error SHALL name
each unresolved reference, and SHALL be shown in the chat and given to the agent on its next
turn.

#### Scenario: Missing component definition

- **WHEN** the agent replies `root = VBox([title, chart])` and does not define `chart`
- **THEN** the UI is unchanged and the chat shows an error that names `chart`

#### Scenario: Unquoted callback handler

- **WHEN** a statement binds an action to a bare name that the program does not define
- **THEN** the UI is unchanged and the error names that statement and the unresolved name

### Requirement: Malformed children are reported by statement

A child that is not a component SHALL produce a generation error that names the statement that
holds it.

#### Scenario: String used as a child

- **WHEN** the program contains `box = VBox(["hello"])`
- **THEN** the reply is not applied and the error names statement `box`

### Requirement: The catalog follows constructor signatures

The catalog's props, their types, and their fixed option values SHALL come from each widget
constructor's signature and declared types. Rewording a docstring SHALL NOT change which props or
values the catalog accepts, and every option value the catalog lists SHALL be accepted by the
constructor.

#### Scenario: Docstring reworded

- **WHEN** the parameter descriptions in a widget's docstring are rewritten without changing its
  signature
- **THEN** the catalog entry lists the same props, types, and option values

#### Scenario: Every listed option value constructs

- **WHEN** each component is built once per option value its catalog entry lists
- **THEN** every construction succeeds
