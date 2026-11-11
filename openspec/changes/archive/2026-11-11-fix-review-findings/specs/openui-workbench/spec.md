# Spec Delta

## Purpose

A notebook workbench that pairs an agent chat with a live, generated anylumino UI, and shows the
OpenUI program, generated UI code, and callbacks behind it, with named sessions that survive
kernel restarts.

## ADDED Requirements

### Requirement: The workbench recovers from any failed operation

When a turn, an import, or a restore fails for any reason, the workbench SHALL show a system
message that names the failure, SHALL leave the UI unchanged, and SHALL return to the idle state
so the next submit or import is accepted.

#### Scenario: Import of a file that is not valid UTF-8

- **WHEN** the user imports a `.py` file that cannot be decoded as UTF-8
- **THEN** the chat shows that the import failed and why, the status is idle, and a following
  submit starts a turn

#### Scenario: Unexpected error inside a turn

- **WHEN** a turn raises an error the workbench does not anticipate
- **THEN** the chat shows the error, the status is idle, and the UI is unchanged

### Requirement: One outcome per turn

Each turn SHALL end with exactly one outcome: applied, not applied, failed, or stopped. Messages
that depend on the outcome SHALL match it, and tool calls of a turn that did not complete SHALL
NOT stay marked as running.

#### Scenario: Agent failure during a reconcile turn

- **WHEN** a reconcile turn ends because the agent failed
- **THEN** the chat shows the failure and does not also ask the agent to close a remaining gap

#### Scenario: Turn stopped while a tool runs

- **WHEN** the user stops a turn while a tool call is in progress
- **THEN** that tool call is marked `error`, in the chat and in the saved session, and the reply
  is marked stopped; the chat component has no stopped state for a tool call

#### Scenario: Stop during apply

- **WHEN** the user stops a turn after the agent replied and before the reply is applied
- **THEN** the reply is not applied and the turn ends as stopped

### Requirement: Explicit working directory overrides the saved one

When a workbench is created for an existing session with an explicit `cwd`, the session SHALL use
and save that directory. Without an explicit `cwd`, it SHALL use the saved directory.

#### Scenario: Project directory moved

- **WHEN** `Workbench(session="x", cwd=new_dir)` is created and session `x` was saved with a
  directory that no longer exists
- **THEN** turns run in `new_dir` and the session file records `new_dir`

#### Scenario: No cwd given

- **WHEN** `Workbench(session="x")` is created for a saved session
- **THEN** turns run in the saved directory

### Requirement: Taking over a session stops its running turn

When a workbench is created for a session on which another workbench in the same kernel has a
turn running, that turn SHALL be stopped and its agent process terminated before the new
workbench starts a turn.

#### Scenario: Cell rerun during a turn

- **WHEN** the cell that creates `Workbench(session="x", prompt=...)` is run again while its
  first turn is still streaming
- **THEN** the first turn's agent process ends, one turn runs for session `x`, and the session
  file holds that turn's result

### Requirement: Chat updates are not lost

A system message added while a reply is streaming SHALL remain in the chat, in every supported
notebook host.

#### Scenario: Message during streaming in marimo

- **WHEN** a callback error is reported while a turn streams its reply in marimo
- **THEN** the chat shows both the error message and the complete reply
