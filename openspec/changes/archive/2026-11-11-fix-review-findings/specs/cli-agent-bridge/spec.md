# Spec Delta

## Purpose

Runs a local coding agent CLI as a subprocess for one workbench turn and turns its output into
streamed text, tool activity, and a final result or failure.

## ADDED Requirements

### Requirement: The first failure is reported

When an agent reports an error and its process then exits with a non-zero status, the failure
shown to the user SHALL be the agent's own error text. The exit status SHALL be reported only when
the agent gave no error of its own.

#### Scenario: Error result followed by a non-zero exit

- **WHEN** the CLI emits an error result with the text `Credit balance is too low` and exits
  with status 1
- **THEN** the chat shows `Credit balance is too low`

#### Scenario: Non-zero exit with no error result

- **WHEN** the CLI exits with status 2 without emitting an error result
- **THEN** the chat shows the exit status and the CLI's standard error text

### Requirement: An early exit reports the CLI's error output

When the CLI exits before it has read its whole prompt, the failure shown to the user SHALL
contain the CLI's standard error text, for a prompt of any size.

#### Scenario: Rejected argument with a large prompt

- **WHEN** the CLI rejects an argument and exits at once, and the prompt is larger than the pipe
  buffer
- **THEN** the chat shows the CLI's error text and not a broken pipe error
