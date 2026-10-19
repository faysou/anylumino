# Spec Delta

## Purpose

Connects the workbench to the locally installed `claude` and `codex` CLIs, running each chat turn
as a non-blocking subprocess that streams the reply, resumes the agent session, and can be stopped.

## ADDED Requirements

### Requirement: Supported agents

The bridge SHALL support the `claude` and `codex` CLIs found on `PATH`, chosen per session. When
the chosen CLI is missing, the bridge SHALL fail the turn with an error that names the missing
executable.

#### Scenario: Missing executable

- **WHEN** the session uses `codex` and no `codex` executable is on `PATH`
- **THEN** the turn ends with an error naming `codex`, and nothing else changes

### Requirement: Non-blocking turns

Each turn SHALL run as an asynchronous subprocess on the kernel event loop, so the notebook stays
responsive and widget events keep working while a turn runs. Only one turn per workbench SHALL
run at a time.

#### Scenario: Kernel stays responsive

- **WHEN** a turn is running
- **THEN** another notebook cell runs to completion before the turn ends

#### Scenario: Second submit during a turn

- **WHEN** the user submits while a turn is running
- **THEN** no second subprocess starts

### Requirement: Streaming output

The bridge SHALL read the CLI's JSON event stream, and SHALL deliver assistant text deltas,
tool-call starts and ends, the final reply text, and the agent session ID as they arrive.

#### Scenario: Text arrives before the turn ends

- **WHEN** the agent writes a long reply
- **THEN** partial assistant text is delivered before the subprocess exits

### Requirement: Session resume

The first turn of a session SHALL start a new agent session with the generated system prompt and
record its agent session ID. Later turns, including turns after a workbench restore, SHALL resume
that agent session ID from the same working directory, and SHALL resend the system prompt only to
CLIs that do not keep it with the session.

#### Scenario: Resume after restore

- **WHEN** a restored session with a recorded agent session ID sends a turn
- **THEN** the CLI is invoked in resume mode with that ID, and the agent sees the earlier
  conversation

### Requirement: Read-only by default

The bridge SHALL run agents without file-write or shell-write permission by default: Claude with
only read-only tools allowed, and Codex in its read-only sandbox. Turns SHALL never wait on an
interactive permission prompt.

Read-only tools SHALL be allowed without a prompt, so the agent can read files in its working
directory and the component options skill.

#### Scenario: Agent reads the options skill

- **WHEN** the agent reads a component's options file during a turn
- **THEN** the read succeeds

MCP servers from the user's configuration SHALL not be available in a turn. When the bridge cannot
turn them off, the turn SHALL not start.

#### Scenario: Codex MCP servers are off

- **WHEN** the codex configuration enables MCP servers
- **THEN** each turn turns every one of them off

#### Scenario: Write attempt is denied

- **WHEN** the agent tries to edit a file during a turn
- **THEN** the edit is not performed and the turn still completes

### Requirement: Stop a turn

The bridge SHALL stop a running turn on request by terminating the subprocess. Stopping SHALL keep
the previous program and callbacks, and SHALL mark the partial assistant message as stopped.

#### Scenario: Stop mid-reply

- **WHEN** the user stops a turn that has streamed partial text
- **THEN** the subprocess exits, the UI tabs are unchanged, and the partial message is marked
  stopped

### Requirement: Reply splitting

The bridge SHALL split the final reply into the prose shown in the chat, at most one fenced
`openui` program, and at most one fenced `python` callbacks block. A missing block SHALL mean
that part is unchanged for this turn. A reply with more than one block of either kind SHALL be
rejected with an error.

#### Scenario: Prose with both blocks

- **WHEN** the reply is prose followed by one `openui` fence and one `python` fence
- **THEN** the chat shows only the prose, and the program and callbacks are taken from the fences

#### Scenario: Callbacks-only change

- **WHEN** the reply contains a `python` fence and no `openui` fence
- **THEN** the current program is kept and only the callbacks change
