# Design

## Context

See `proposal.md` for the motivation. The facts below constrain the design.

- **Astryx wrappers:**
  - Python classes subclass `Widget` (`src/anylumino/astryx/base.py:324`), which subclasses
    `ComponentWidget` (`src/anylumino/components.py:22`).
  - Props reach the frontend through the `props` dict.
  - Events arrive as custom messages handled in `_handle_frontend_message`
    (`components.py:107`, `base.py:492`).
  - `tests/test_widgets.py:1390` requires every frontend message type to be handled.
  - `astryx_widget.js` maps component names to React components (`COMPONENTS`, line 123) and
    builds props per name (`componentProps`, line 704).
- **No single Chat component:** `@astryxdesign/core` 0.6.2 has no `Chat` component. It ships
  `ChatLayout`, `ChatMessageList`, `ChatMessage`, `ChatMessageBubble`, `ChatSystemMessage`,
  `ChatToolCalls`, and `ChatComposer`. Their slots take React nodes, so the frontend must
  assemble them.
- **Layouts:**
  - Layouts take `widgets` as a list or as a mapping of key to widget, plus `titles`
    (`src/anylumino/layout.py:448`).
  - `TabPanel.selected_index` syncs both ways (`layout.py:543`, `tab_panel.js:154`).
  - Callbacks register through `on_click(cb)` and `on_action(cb)` (`src/anylumino/common.py:47`).
    These deliver `cb(widget)` and `cb(widget, value)`.
- **OpenUI** (thesysdev/openui, MIT, cloned in `MiscRepos/openui`): `@openuidev/lang-core` 1.0.1
  is TypeScript only, and there is no Python port.
  - `createParser(libraryJSONSchema)` parses without React or Zod
    (`packages/lang-core/src/parser/parser.ts:749`).
  - `mergeStatements(existing, patch)` applies edit-mode patches (`parser/merge.ts:141`).
  - `generateSystemPrompt({library: LibrarySpec, ...})` builds the prompt from a JSON library
    spec (`parser/prompt.ts:769`).
  - Custom actions reach the host as `{type, params}` (`spec/language.md` section 6.3).
  - The conformance fixtures are in `spec/fixtures/1.0/`.
- **Agent CLIs:** the installed versions are Claude Code 2.1.302 and codex-cli 0.163.0.
  - `claude -p` supports `--output-format stream-json`, `--include-partial-messages`,
    `--session-id <uuid>`, `--resume <id>`, `--append-system-prompt`, `--allowedTools`, and
    `--tools`.
  - `-n` only sets a display name. In print mode, `--resume` takes a session ID.
  - `codex exec` supports `--json` (JSONL events), `-s read-only`, `-C <dir>`, and
    `--skip-git-repo-check`. `codex exec resume <id> <prompt>` resumes a session. Codex has no
    flag to append a system prompt.
- **anywidget:** anylumino pins `anywidget>=0.11.0` from PyPI (`uv.lock`), and CI runs `uv sync`.
  - In `../anywidget`, `WidgetBinding.createView` (`packages/anywidget/src/binding.ts:83`)
    calls `render` with `target.el` straight after `await this.ready`. This is
    manzt/anywidget#1025.
  - anylumino layouts work around it with `whenConnected`
    (`src/anylumino/static/layout/composition.js:174`).

## Goals / Non-Goals

**Goals:**

- One path from an agent reply to the live UI: merge, parse, generate Python, then run that
  Python. The `UI code` tab is the code that runs.
- Python tests can check every step without a browser, apart from rendering.
- Keep the current anylumino install and CI unchanged for users who do not use the workbench.

**Non-Goals:**

- Editing code tabs by hand. The design keeps this possible, as described in the editable-tabs
  decision.
- OpenUI `$state`, `Query`, `Mutation`, forms, or `@Each`. The prompt does not teach them.
  Programs that use them fail code generation with a named error.
- Streaming the UI while a turn runs. The UI changes once per turn.
- Changing the agent mid-session.

## Decisions

### OpenUI Lang, not a custom JSON schema

The draft's `openui-json` format would need its own grammar, prompt, validation, and patching.
OpenUI Lang already has these, including a normative spec and fixtures. The format is also
cheaper in tokens than JSON, and edit mode lets a follow-up turn send only the statements that
changed.

wandb/openui generates HTML and JSX, and has no spec language to show in a tab, so it does not
fit.

### Parse with the official parser under Node

`scripts/openui_tool.mjs` imports `@openuidev/lang-core` and is bundled by esbuild into
`src/anylumino/static/openui/openui_tool.bundle.mjs` with `platform: "node"`. It reads one JSON
request on stdin and writes one JSON response on stdout, for three commands:

- `parse`: takes `{program, library}` and returns the tree, errors, and statements;
- `merge`: takes `{current, patch}` and returns the merged program text;
- `prompt`: takes `{library, options, extra}` and returns the prompt text.

Python calls it once per turn with `asyncio.create_subprocess_exec("node", ...)`.

The alternatives each had a blocking problem:

| Alternative                                  | Problem                                                                                                       |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Python port of the parser                    | About 2.2k lines of TypeScript to port and track. Deferred: the fixtures would let a port prove itself later. |
| Parse in the browser through the widget      | Needs a rendered view, so a session restore before display and headless tests would fail.                     |
| Embedded JS engine (`mini-racer`, `quickjs`) | Adds a binary dependency with uncertain Python 3.14 wheels.                                                   |

The agent CLIs already make this a developer tool, so requiring Node on `PATH` is acceptable.
The workbench checks for `node` when it is created and names it in the error.

Pin `@openuidev/lang-core` and `zod` to exact versions. They do not join `allowScripts`, so no
install script runs. The bundle has to keep its telemetry off: the install telemetry runs only as
an install script, and the runtime telemetry is opt-in.

### The catalog lives in Python, and the library spec is derived from it

`src/anylumino/workbench/catalog.py` maps each OpenUI component name to the following:

- the anylumino class;
- a description;
- ordered props, each with a JSON Schema type and a required flag;
- which props are child slots;
- which props are action slots, and the event each one binds to.

Prop names match the Python constructor keywords, so code generation copies them through.

The catalog's `VBox` and `HBox` build an Astryx `ax.Stack` (CSS flex), not a Lumino box. A
browser check showed that Lumino boxes split their height evenly between stretch-0 children, even
with `fit_content`, which clipped tables and text. A stack lays out its children at natural size,
and the `UI` tab host is a `ScrollBox`, so a tall UI scrolls. `SplitPanel` and `TabPanel` stay
Lumino with their default height. The
catalog emits the OpenUI LibrarySpec JSON (`spec/prompt.md` section 2), including the
`Callback` custom action.

No Zod definitions exist, because `createParser` and `generateSystemPrompt` both accept JSON.
The catalog lives next to the classes it describes, which keeps one definition. A test builds
each catalog entry's widget, so a renamed keyword fails the test.

The prompt is generated when the workbench needs it and cached by catalog hash, so no generated
prompt file is committed. The workbench adds a prompt section with the callback contract and the
namespace summary.

### Code generation replaces the draft's interpreter

`codegen.py` walks the parsed tree and emits a module. The draft had both an interpreter and an
exporter, which could drift apart. Here the live UI runs the generated source with `exec` in a
fresh module namespace, so what the tab shows is what runs.

The generated module defines a `UI` class:

```python
import anylumino as al
import anylumino.astryx as ax


class UI(View):
    def __init__(self, app):
        self.app = app
        self.title = ax.Heading(text='Sales')
        self.go = ax.Button(label='Run', variant='primary')
        self.root = ax.Stack(children=[self.title, self.go], direction='vertical')

        def go_action(_widget, value=None):
            app.call('on_run', Event('go', value, 'q3'))

        self.go.on_click(go_action)

        self.widget = self.root
        app.set_ui(self)
```

Statement names become attributes. Statements are emitted children before parents, in the stable
order of `spec/language.md` section 9.2, which keeps the output deterministic. Literal props are
written with `repr`. A prop that holds a dynamic AST node is a generation error that names the
statement.

### The callbacks are an App subclass that controls the UI

Programs bind events with `@Callback(handler, context?)`. The fenced `python` block defines one
subclass of `anylumino.workbench.App` with a `handler(self, event)` method per handler, where
`event` is `{"source", "value", "context"}`, and an optional `setup(self)`. `@ToAssistant` maps to
`app.ask_agent`.

`App` is a plain class that holds the data and handlers. The generated `UI(app)` is a `View`: a
plain object with one attribute per statement and the root widget as `widget`. It is not a widget,
so statement names cannot collide with widget members; only `app` and `widget` are taken.
anylumino containers accept any object with a `.widget`, so the UI still composes as a tab, a
split side, or a child of another UI, and a cell shows it through `_repr_mimebundle_`. The `UI`
constructor calls `app.set_ui(self)`, which keeps it as `app.ui` and runs `setup`, so a `UI`
builds headless in tests. One app drives one UI: a second `set_ui` raises, since the first UI's
handlers would otherwise change the second. Handlers receive an immutable `Event` with
`source`, `value`, and `context` attributes rather than a dict.

The namespace reaches the app as constructor keywords, `SalesApp(sales=sales)`, and handlers read
`self.sales`. The callbacks run in a module without notebook globals, so an exported pair of files
works as an ordinary module, and the caller passes the data explicitly. A namespace name that is
not an identifier or that an `App` member uses is rejected, and so is a handler that replaces an
`App` member other than `setup`, since a method named `call` or `ui` would break the app.

Export writes one module: the UI code first, then the callbacks, with the callbacks' leading
imports moved up. One file is simpler to move and import than a pair, and `UI` only needs `app` at
call time, so it can come before the `App` subclass.

`app.call` runs a handler and passes an exception to `app.on_error` when set; the workbench sets it
to post the error in the chat. `app.ask_agent` calls `app.agent`, which the workbench sets; outside
a workbench it warns. This keeps the OpenUI action model instead of the draft's `on_click` and
`on_change` props. The catalog decides the event per action slot, so the agent does not need to
know about `clicks` or `value` traits.

### Edit mode always merges

The prompt teaches edit mode, so every `openui` fence is merged into the current program. A full
program merges to itself, because each name is replaced and unreachable statements are dropped.
This needs no "patch or full" detection.

The callbacks fence always replaces the whole callbacks module, since Python has no
statement-level merge.

### Component options come from the wrappers, documented in a skill

Each catalog component ends with an optional `options` object instead of more positional props.
OpenUI Lang arguments are positional, and long runs of `null` before an option are easy for an
agent to get wrong. The option keys come from the wrapper's constructor keywords that the
positional props do not cover, with types from the annotations and descriptions from the numpydoc
`Parameters` section. A new wrapper keyword reaches the agent without a catalog edit. The parser
type-checks values but accepts unknown keys, so code generation rejects them.

The 156 options would roughly double the system prompt, so the prompt keeps only the signatures
and points to the `openui-components` skill. `make workbench-skill` writes it into
`src/anylumino/workbench/plugin/`, a Claude Code plugin directory that ships in the wheel. Claude
loads it with `--plugin-dir`. Codex has no per-run skill path, and moving `CODEX_HOME` would lose
its sign-in, so the prompt also gives the absolute path of the files, which Codex reads from its
read-only sandbox. Live turns on 2026-10-19 showed both CLIs reading `Table.md` and passing
`{sortable: true}`.

### Agent invocations

Both CLIs run in the session's working directory, which defaults to the notebook's current
directory and is stored in the session. The prompt goes on stdin.

- **Claude, first turn:** `claude -p --output-format stream-json --verbose
  --include-partial-messages --session-id <uuid> -n <session> --append-system-prompt <prompt>
  --plugin-dir <package plugin> --tools Read,Grep,Glob,Skill --allowedTools Read,Grep,Glob,Skill
  --permission-mode dontAsk`.
  - `--tools` removes every other tool.
  - `dontAsk` denies every tool that no allow rule approves, including the listed tools, so
    `--allowedTools` approves them. A live turn without it had every read and search denied.
  - `--plugin-dir` loads the component options skill for this run only.
  - `--tools` does not remove MCP tools, so `--strict-mcp-config` keeps the user's MCP servers out.
- **Claude, later turns:** the same flags with `--resume <uuid>` in place of `--session-id` and
  `-n`. `--append-system-prompt` applies to one invocation only, so every turn sends it again.
- **Codex, first turn:** `codex exec --json -s read-only --skip-git-repo-check -C <cwd>
  -c developer_instructions=<prompt> -`.
- **Codex, later turns:** `codex exec resume <thread_id> --json --skip-git-repo-check
  -c sandbox_mode="read-only" -`.
- **Codex MCP servers:** both forms add one `-c` override per enabled server from
  `codex mcp list --json`, because the read-only sandbox does not cover MCP tools such as browser
  control. The override replaces the server with a disabled placeholder transport, for example
  `mcp_servers.graft={command="true",enabled=false}`. Plugin servers have no `config.toml` entry,
  so `enabled=false` alone left them without a transport and codex refused to start.
  `-c mcp_servers={}` merges instead of replacing, and `--ignore-user-config` would also drop the
  user's model settings. Codex splits override keys on dots and rejects quoted keys, so a server
  name outside `[A-Za-z0-9_-]`, an unknown transport type, or an unreadable list fails the turn.
- **Claude stream:** the `system/init` event gives the session ID. `text_delta` stream events give
  text. `assistant` messages give tool calls with their input, and `user` tool results end them.
- **Codex stream:** `thread.started` gives the thread ID. Completed `agent_message` items give
  text, since there are no partial deltas. Other items start and end tool rows.

Claude needs a session ID that the workbench creates, because `-n` cannot be resumed reliably in
print mode, which the draft assumed. Codex reports its thread ID in the first event, and the
workbench saves it at once.

Stop sends SIGTERM to the process group, then SIGKILL after a grace period. The stream parsers are
pure classes over event lines. Tests replay streams captured from Claude Code 2.1.302 and
codex-cli 0.163.0 (`tests/fixtures/agents/`) through fake executables placed on `PATH`.

### Chat is one Astryx component assembled in the frontend

Add a `Chat` case to `astryx_widget.js` that builds `ChatLayout`, `ChatMessageList`, and the
messages from Python. Each message renders as a `ChatMessage` with a `ChatMessageBubble` that wraps
the Markdown renderer already used by `ax.Markdown`. System rows use `ChatSystemMessage`, and tool
calls use `ChatToolCalls`. The composer is a `ChatComposer` with stop shown while streaming.

On the Python side, `ax.Chat` has these traits: `messages` (a list of dicts with `role`,
`content`, `status`, and `tool_calls`), `is_streaming`, `placeholder`, and `disabled`. It handles
`{type: "submit", value}` and `{type: "stop"}`, and exposes `on_submit(cb)` and `on_stop(cb)`.

Streaming replaces the last message in `messages`. The bridge sends at most one update per frame:
it coalesces deltas on a short timer, so a long reply does not flood the comm channel.

### Workbench assembly

`Workbench` is an `al.SplitPanel`:

- **Left:** an `al.VBox` with a header row (agent, session, `ax.StatusDot` for the turn state)
  and the `ax.Chat`.
- **Right:** an `al.TabPanel` keyed `ui`, `openui`, `ui_code`, and `callbacks`.
  - The `UI` tab is a host panel whose single child is swapped on apply, with an
    `ax.EmptyState` before the first turn.
  - The three code tabs are read-only `ax.CodeBlock`s, with language `python` for the two
    Python tabs.

A turn is applied in this order: split, merge, parse, compile the callbacks, generate the UI code,
build. Every step writes to local variables. Only after the build succeeds does the workbench
assign the four tab contents and swap the UI child.

### Session store

Sessions are saved to `~/.anylumino/sessions/<session>.json` by writing a temporary file and
renaming it. The draft used `~/.anylumino_sessions`; nesting under `~/.anylumino` leaves room for
other state.

The UI code is not stored, because it is derived. On restore, it is regenerated from the program.

Session names are limited to `[A-Za-z0-9_-]+`, so they cannot escape the directory.

### Editable tabs later, without rework

The program and the callbacks are the only sources, and the UI code is derived. A later change can
make the `OpenUI` and `Callbacks` tabs editable and rerun "apply" from them. That path can reuse
the atomic apply and its error reporting. Editing `UI code` by hand would need a reverse mapping to
OpenUI, through the serializer in `spec/language.md` section 9.2, and stays out of scope until
then.

### anywidget#1025 in the local clone

On a branch of `../anywidget` cut from `origin/main`, `createView` waits for an attached target
before it calls `render`:

- render at once if `target.el.isConnected`;
- otherwise check `isConnected` again whenever `target.displayed` resolves (ipywidgets views) or an
  animation frame passes, and give up when the combined abort signal fires.

`displayed` is raced with the frame poll rather than awaited first: a host that appends `view.el`
without triggering `displayed` would otherwise wait forever. `host.getWidget(ref).render({el})`
goes through the same `createView`, so the same wait covers it without a change to `host.ts`.
Tests go in the clone's existing test suite.

anylumino uses the clone through a new `make install-dev-anywidget-local` target. The target
builds the clone's frontend, then runs `uv pip install -e ../anywidget` into the anylumino
environment. Later commands use `uv run --no-sync`.

`pyproject.toml` and `uv.lock` are unchanged, so CI and published wheels keep PyPI anywidget.
`whenConnected` stays, because released anywidget still has the race. The fix is proposed
upstream as manzt/anywidget#1029; `whenConnected` can go once a release includes it.

### Testing

| Layer                   | Tool                                                                                          | What it covers                                                                                                           |
| ----------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Catalog, codegen, apply | pytest                                                                                        | Exact-source snapshots, executed builds, and callback dispatch through `_handle_frontend_message`                        |
| Bridge                  | pytest with fake `claude` and `codex` scripts on `PATH`                                       | Recorded streams, resume arguments, stop, and a missing executable                                                       |
| OpenUI tool             | `node --test`                                                                                 | The bundle, run against a few OpenUI conformance fixtures copied into `tests/frontend/fixtures/openui/`                  |
| Rendering and layout    | ego-lite (ego-browser skill), against `uv run --no-sync jupyter lab` started from `anylumino` | Rendering, tab switching, read-only code tabs, and chat submit and stop, using a percent-format notebook in `notebooks/` |
| Live agents             | One smoke turn per CLI in that notebook                                                       | The real `claude` and `codex` calls. These run only on request, because they spend tokens.                               |

## Risks / Trade-offs

- **[Agent code runs in the kernel]** The callbacks and the UI code are executed. Mitigations:
  the workbench is for local use with the user's own agent; agent tools are read-only; the code is
  always visible in the tabs before the user interacts with it; the docs state the risk.
- **[CLI flag or event drift]** The stream formats are not a stable API. Mitigations: the parsers
  sit in one module per CLI; the fakes replay streams captured from the tested versions
  (Claude Code 2.1.302, codex-cli 0.163.0); an unknown event type is ignored, not fatal.
- **[lang-core 1.x API change]** Pin the exact version, and test the bundle against fixtures.
- **[Prompt size]** The generated prompt grows with the catalog. Keep the catalog to the listed
  components and measure the prompt size in a test.
- **[Node missing]** The workbench fails fast with a message. The rest of anylumino is unaffected.
- **[Local anywidget drift]** `uv sync` without `--no-sync` reinstalls PyPI anywidget. The Make
  target and the docs say to use `--no-sync` after installing the clone.

## Migration Plan

This change is additive. `docs/openui.md` stays as the original draft, and this change supersedes
it. Rollback means removing the `workbench` package, `astryx/chat.py`, the `Chat` frontend case,
and the OpenUI bundle entry.

## Resolved Questions

- **Claude permission mode:** `--permission-mode dontAsk` combined with `--tools Read,Grep,Glob`.
  A turn never prompts, and the agent has no tools beyond those three.
- **Codex system prompt:** `-c developer_instructions=<prompt>` on the first turn. It persists
  across `exec resume`.
