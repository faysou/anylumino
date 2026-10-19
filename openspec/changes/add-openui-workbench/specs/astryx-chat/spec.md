# Spec Delta

## Purpose

An Astryx chat widget for notebooks: Python owns the message list and turn state, and the
frontend renders it with the Astryx Chat parts and reports what the user submits or stops.

## ADDED Requirements

### Requirement: Python-owned message list

The `Chat` widget SHALL render its messages from a synced list, where each message has a `role`
(`user`, `assistant`, or `system`), Markdown `content`, and an optional `status` (`sending`,
`sent`, or `error`). Assistant and user messages SHALL render as chat bubbles with Markdown;
system messages SHALL render as system rows.

#### Scenario: Messages render in order

- **WHEN** Python sets three messages with roles user, assistant, and system
- **THEN** the view shows a user bubble, an assistant bubble with rendered Markdown, and a system
  row, in that order

#### Scenario: Appending a message updates the view

- **WHEN** Python appends a message to a displayed chat
- **THEN** the view shows the new message without re-creating the existing ones

### Requirement: Streaming assistant content

The widget SHALL let Python replace the content of the last assistant message while a turn is
streaming, and SHALL show a streaming state until Python ends the turn.

#### Scenario: Partial text grows in place

- **WHEN** a turn is streaming and Python updates the last assistant message from `Hel` to `Hello`
- **THEN** the same bubble shows `Hello` and the list stays scrolled to the newest content

### Requirement: Submit and stop events

The composer SHALL send the entered text to Python on submit and clear itself. While a turn is
streaming, the composer SHALL show a stop control, and SHALL send a stop event when it is used.
Python SHALL receive submit and stop through registered callbacks.

#### Scenario: Submitting text

- **WHEN** the user types `Add a slider` and submits
- **THEN** every registered submit callback receives the chat and `Add a slider`, and the composer
  is empty

#### Scenario: Submitting while disabled

- **WHEN** Python has disabled the composer and the user presses Enter
- **THEN** no submit callback runs

#### Scenario: Stopping a turn

- **WHEN** a turn is streaming and the user uses the stop control
- **THEN** every registered stop callback runs once

### Requirement: Tool-call activity

The widget SHALL display, under an assistant message, a list of tool calls with a name, an
optional target, and a status (`pending`, `running`, `complete`, or `error`) that Python can
update.

#### Scenario: Tool call completes

- **WHEN** Python adds a `Read` tool call with target `sales.csv` and status `running`, then sets
  it to `complete`
- **THEN** the view shows one `Read sales.csv` row whose status changes from running to complete
