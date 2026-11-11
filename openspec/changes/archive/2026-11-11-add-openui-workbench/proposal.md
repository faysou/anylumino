# Proposal

## Why

anylumino can lay out Astryx and Lumino widgets in a notebook, but building such a UI still means
writing the widget tree and its event handlers by hand. A notebook workbench, where a chat with a
local coding agent (`claude` or `codex`) generates the UI and its callbacks, makes UI building
conversational. The workbench also shows every artifact behind the live UI: the OpenUI program, the
generated Python, and the callbacks.

The draft in `docs/openui.md` invents its own `openui-json` format. This change uses the actual
OpenUI Lang standard (thesysdev/openui, MIT) instead. That gives the agent a documented language,
a system prompt generated from our component catalog, a conformance-tested parser, and incremental
edits.

## What Changes

- Add `anylumino.astryx.Chat`: a chat widget built from the `@astryxdesign/core` Chat parts
  (message list, Markdown bubbles, tool-call rows, composer with send and stop). Python drives
  its messages and receives submit and stop events.
- Add `anylumino.workbench.Workbench`: a horizontal split. The chat is on the left. On the right is
  a tab panel with four tabs: `UI` (live widgets), `OpenUI` (program text), `UI code` (generated
  Python), and `Callbacks` (agent-written Python). Code tabs are read-only in this change, and only
  chat turns change them.
- Add an OpenUI catalog of anylumino components. The library spec and the agent system prompt are
  generated from it.
- Add a bundled OpenUI Lang tool. It parses and merges programs with `@openuidev/lang-core` and
  runs under Node from Python.
- Add deterministic code generation from the parsed OpenUI tree to Python that builds anylumino
  widgets and wires `@Callback(...)` actions to the callbacks. The live `UI` tab runs exactly the
  code that the `UI code` tab shows.
- Add a local agent bridge for the installed `claude` and `codex` CLIs. It streams replies into the
  chat, resumes sessions by agent session ID, gives read-only tool access by default, and lets the
  user stop a turn.
- Add named sessions persisted as JSON. A new `Workbench(session="name")` restores the chat, the
  program, the callbacks, and the live UI, and resumes the agent session.
- In the local anywidget clone (`../anywidget`), fix manzt/anywidget#1025 so `render` receives an
  attached `el`. Add a Make target that installs that clone into the anylumino dev environment for
  workbench development.
- Out of scope, kept as a stated later objective: editing the code tabs by hand and regenerating
  the other tabs from the edit.

## Capabilities

### New Capabilities

- `astryx-chat`: the Astryx chat widget, covering its messages, streaming, tool-call display, and
  submit and stop events.
- `openui-codegen`: the OpenUI catalog, system prompt, parsing and merging of OpenUI Lang
  programs, and generation of Python UI code bound to callbacks.
- `cli-agent-bridge`: running the local `claude` and `codex` CLIs per chat turn, covering
  streaming, session resume, stop, permissions, and reply splitting.
- `openui-workbench`: the workbench layout, the four tabs, applying a turn atomically, notebook
  namespace access, and session persistence and recovery.

### Modified Capabilities

None. The repository has no existing specs.

## Impact

- **New Python modules** under `src/anylumino/workbench/`, and a new `Chat` class in
  `src/anylumino/astryx/`.
- **Frontend:**
  - `astryx_widget.js` gains the `Chat` component.
  - A new Node entry is bundled to `src/anylumino/static/openui/`.
  - `package.json` gains `@openuidev/lang-core` and `zod`.
- **Runtime requirements:** the workbench, and only the workbench, needs `node` on `PATH` plus the
  chosen agent CLI. The rest of anylumino keeps its current dependencies.
- **Agent-written code runs in the kernel:** callbacks and generated UI code run with the
  workbench namespace, by design.
- **anywidget:** the published dependency stays `anywidget>=0.11.0`. The connection wait in
  anylumino (`whenConnected`) stays, because released anywidget lacks the fix. The fork is used
  only through an opt-in local install, so CI and the lock file still resolve anywidget from PyPI.
- **Testing:** browser checks run with ego-lite against JupyterLab started from anylumino with
  `uv run`.
