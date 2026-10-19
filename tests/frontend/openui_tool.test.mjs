import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import test from "node:test";

// Cases copied from the OpenUI 1.0 conformance fixtures (MIT, see fixtures/openui/LICENSE).
const FIXTURES = new URL("./fixtures/openui/", import.meta.url);
const TOOL = new URL("../../src/anylumino/static/openui/openui_tool.bundle.mjs", import.meta.url);
const library = JSON.parse(readFileSync(new URL("library.json", FIXTURES), "utf8"));
const actionParams = Object.fromEntries(
  Object.entries(library.schema.actions).map(([name, action]) => [name, Object.keys(action.params.properties)]),
);


function run(request) {
  const output = execFileSync("node", [TOOL.pathname], {
    input: JSON.stringify(request),
    env: { ...process.env, OPENUI_TELEMETRY_DISABLED: "1" },
  });
  return JSON.parse(output.toString());
}

function read(name, file) {
  return readFileSync(new URL(`${name}/${file}`, FIXTURES), "utf8");
}

// The tree summary of the fixtures README, for programs without state or queries.
function summarizeStep(step) {
  if (step.type === "continue_conversation") {
    return { action: "ToAssistant", args: step.context == null ? [step.message] : [step.message, step.context] };
  }
  return { action: step.name, args: actionParams[step.name].map((key) => summarize(step.params[key])) };
}

function summarize(value) {
  if (value == null || typeof value !== "object") {
    return value ?? null;
  }
  if (Array.isArray(value)) {
    return value.map(summarize);
  }
  if (value.type === "element") {
    const props = Object.entries(value.props)
      .map(([key, prop]) => [key, summarize(prop)])
      .filter(([, prop]) => prop !== null);
    return { type: value.typeName, props: Object.fromEntries(props) };
  }
  if (Array.isArray(value.steps)) {
    return { actions: value.steps.map(summarizeStep) };
  }
  return Object.fromEntries(Object.entries(value).map(([key, prop]) => [key, summarize(prop)]));
}

function check(name, program) {
  const expected = JSON.parse(read(name, "expected.json"));
  const result = run({ command: "parse", program, library });
  assert.deepEqual(summarize(result.root), expected.root);
  assert.deepEqual(
    result.errors.map(({ code, statementId }) => ({ code, statementId })),
    expected.errors,
  );
  assert.deepEqual(result.unresolved, expected.unresolved);
  assert.deepEqual(result.orphans, expected.orphans);
  assert.equal(result.incomplete, expected.incomplete);
  return { expected, result };
}


for (const name of ["grammar/004-comment-strip", "actions/009-custom-action", "errors/001-unknown-component-dropped"]) {
  test(`parse matches the ${name} fixture`, () => {
    check(name, read(name, "input.oui"));
  });
}

for (const name of ["editing/001-replace-and-add", "editing/005-fenced-patch"]) {
  test(`merge matches the ${name} fixture`, () => {
    const { program } = run({ command: "merge", current: read(name, "input.oui"), patch: read(name, "patch.oui") });
    const { expected, result } = check(name, program);
    assert.deepEqual(result.statements, expected.statements);
  });
}

test("parse reports statement names, state, and queries", () => {
  const result = run({
    command: "parse",
    program: 'root = Stack([t])\nt = Text("a")\n$sel = "a"',
    library,
  });
  assert.equal(result.root.statementId, "root");
  assert.equal(result.root.props.children[0].statementId, "t");
  assert.deepEqual(result.statements, ["root", "t", "$sel"]);
  assert.deepEqual(result.states, ["$sel"]);
  assert.deepEqual(result.queries, []);
  assert.deepEqual(result.mutations, []);
});

test("merge without a current program returns the patch", () => {
  assert.deepEqual(run({ command: "merge", current: "", patch: 'root = Text("a")' }), {
    program: 'root = Text("a")',
  });
});

test("prompt documents the library components", () => {
  const { prompt } = run({ command: "prompt", library, options: { inlineMode: true, editMode: true } });
  assert.match(prompt, /Stack\(children: any\[\], direction\?: "row" \| "column"\)/);
  assert.match(prompt, /CopyToClipboard\(text: string\)/);
});

test("an unknown command exits with status 2", () => {
  assert.throws(
    () => execFileSync("node", [TOOL.pathname], { input: '{"command": "x"}', stdio: "pipe" }),
    (error) => error.status === 2 && error.stderr.toString() === "Unknown command: x\n",
  );
});
