// Reads one JSON request on stdin and writes one JSON response on stdout:
//   {"command": "parse", "program", "library"} -> evaluated tree, errors, statements
//   {"command": "merge", "current", "patch"} -> merged program text
//   {"command": "prompt", "library", "options"} -> system prompt text
import {
  createLibrary,
  createParser,
  createStore,
  defineComponent,
  evaluate,
  evaluateRoot,
  generateSystemPrompt,
  mergeStatements,
} from "@openuidev/lang-core";
import * as z from "zod/v4";

const STATEMENT = /^(\$?\w+)\s*=(?!=)/;

// Evaluation only needs each component's prop keys; parsing uses the JSON schema as it is.
function evaluationLibrary(spec) {
  const library = createLibrary({
    components: Object.entries(spec.components).map(([name, { description }]) => {
      const keys = Object.keys(spec.schema.$defs[name]?.properties ?? {});
      return defineComponent({
        name,
        description: description ?? "",
        props: z.object(Object.fromEntries(keys.map((key) => [key, z.any()]))),
        component: null,
      });
    }),
    root: spec.root,
  });
  return { ...library, toJSONSchema: () => spec.schema };
}

function parse({ program, library: spec }) {
  const result = createParser(spec.schema, spec.root).parse(program);
  const store = createStore();
  store.initialize(result.stateDeclarations ?? {}, {});
  const ctx = {
    getState: (name) => store.get(name) ?? null,
    resolveRef: () => null,
    actions: spec.schema.actions,
  };
  const runtimeErrors = [];
  const root = evaluateRoot(result, {
    ctx,
    library: evaluationLibrary(spec),
    store,
    errors: runtimeErrors,
  });
  return {
    root,
    errors: [...result.meta.errors.map((e) => ({ source: "parser", ...e })), ...runtimeErrors],
    unresolved: result.meta.unresolved,
    orphans: result.meta.orphaned,
    incomplete: result.meta.incomplete,
    statements: program.split("\n").flatMap((line) => STATEMENT.exec(line)?.[1] ?? []),
    states: Object.keys(result.stateDeclarations ?? {}),
    queries: result.queryStatements.map((s) => s.statementId),
    mutations: result.mutationStatements.map((s) => s.statementId),
  };
}

function merge({ current, patch }) {
  return { program: current ? mergeStatements(current, patch) : patch };
}

function prompt({ library, options }) {
  return { prompt: generateSystemPrompt({ library, promptOptions: options }) };
}

const COMMANDS = { parse, merge, prompt };

let input = "";
for await (const chunk of process.stdin) {
  input += chunk;
}
const request = JSON.parse(input);
const command = COMMANDS[request.command];
if (!command) {
  process.stderr.write(`Unknown command: ${request.command}\n`);
  process.exit(2);
}
process.stdout.write(JSON.stringify(command(request)));
