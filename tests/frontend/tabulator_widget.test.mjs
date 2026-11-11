import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { compileFunction, reviveFunctions } from "../../src/anylumino/static/tabulator/functions.mjs";
import { tableOptions } from "../../src/anylumino/static/tabulator/options.mjs";
import { DELTA, SNAPSHOT, Step, applyDelta, messageRows, nextStep, rebuildsColumns } from "../../src/anylumino/static/tabulator/rows.mjs";

const snapshot = (revision) => ({ type: SNAPSHOT, revision });
const delta = (revision, origin = null) => ({ type: DELTA, revision, op: "update", origin });

for (const [name, revision, content, expected] of [
  ["first snapshot", null, snapshot(0), Step.REPLACE],
  ["newer snapshot", 3, snapshot(5), Step.REPLACE],
  ["stale snapshot", 5, snapshot(5), Step.IGNORE],
  ["delta before the first snapshot", null, delta(1), Step.IGNORE],
  ["next delta", 4, delta(5), Step.APPLY],
  ["delta already in the snapshot", 4, delta(4), Step.IGNORE],
  ["revision gap", 4, delta(6), Step.RESYNC],
  ["own edit echoed back", 4, delta(5, "view-a"), Step.ADVANCE],
  ["edit from another view", 4, delta(5, "view-b"), Step.APPLY],
]) {
  test(`nextStep: ${name}`, () => {
    assert.equal(nextStep(revision, content, "view-a"), expected);
  });
}

test("messageRows: JSON rows", () => {
  assert.deepEqual(messageRows({ rows: [{ id: 1 }] }, []), [{ id: 1 }]);
});

test("messageRows: Arrow stream written by pyarrow", async () => {
  // Written by tests/frontend/fixtures/tabulator/write_rows.py.
  const bytes = await readFile(new URL("./fixtures/tabulator/rows.arrows", import.meta.url));
  const rows = messageRows({ format: "arrow" }, [new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength)]);

  assert.deepEqual(
    rows.map((row) => ({ ...row })),
    [
      { id: 0, symbol: "ESZ6", last: 5012.25, qty: 3, live: true, ts: "2026-11-11T09:30:00", note: null },
      { id: 1, symbol: "NQZ6", last: null, qty: -1, live: false, ts: null, note: "halt" },
    ],
  );
});

test("messageRows: Arrow message without its buffer", () => {
  assert.throws(() => messageRows({ format: "arrow" }, []), /without its buffer/);
});

function fakeTable() {
  const calls = [];
  const record =
    (name) =>
    (...args) => {
      calls.push([name, ...args]);
      return Promise.resolve();
    };
  return {
    calls,
    updateData: record("updateData"),
    addData: record("addData"),
    updateOrAddData: record("updateOrAddData"),
    deleteRow: record("deleteRow"),
  };
}

for (const [op, content, expected] of [
  ["update", {}, ["updateData", [{ id: 1 }]]],
  ["add", { top: true }, ["addData", [{ id: 1 }], true]],
  ["upsert", {}, ["updateOrAddData", [{ id: 1 }]]],
  ["delete", { ids: [4, 5] }, ["deleteRow", [4, 5]]],
]) {
  test(`applyDelta: ${op}`, async () => {
    const table = fakeTable();
    await applyDelta(table, { op, ...content }, [{ id: 1 }]);
    assert.deepEqual(table.calls, [expected]);
  });
}

test("applyDelta: unknown change", () => {
  assert.throws(() => applyDelta(fakeTable(), { op: "move" }, []), /unknown row change move/);
});

test("reviveFunctions: nested formatter and menu action", () => {
  const columns = reviveFunctions(
    [
      {
        field: "px",
        formatter: { $js: "function(cell) { return cell.getValue() + '!'; }" },
        headerMenu: [{ label: "Hide", action: { $js: "(event, column) => column.hide()" } }],
      },
    ],
    "columns",
  );
  let hidden = false;

  columns[0].headerMenu[0].action(null, { hide: () => (hidden = true) });

  assert.equal(columns[0].formatter({ getValue: () => "a" }), "a!");
  assert.equal(hidden, true);
  assert.equal(columns[0].field, "px");
});

test("reviveFunctions: an object with other keys stays an object", () => {
  assert.deepEqual(reviveFunctions({ $js: "x", note: 1 }, "options"), { $js: "x", note: 1 });
});

for (const [name, source, message] of [
  ["syntax error", "not a function (", /^columns\[0\]\.formatter: /],
  ["not a function", "42", /^columns\[0\]\.formatter: the source does not evaluate to a function$/],
]) {
  test(`compileFunction: ${name}`, () => {
    assert.throws(() => compileFunction(source, "columns[0].formatter"), { message });
  });
}

class FakeShadowRoot {}

function fakeRoot(rootNode) {
  return { getRootNode: () => rootNode };
}

test("tableOptions: popups stay in a shadow root", () => {
  globalThis.ShadowRoot = FakeShadowRoot;
  try {
    const root = fakeRoot(new FakeShadowRoot());
    assert.equal(tableOptions({ index: "id" }, root).popupContainer, root);
    assert.equal("popupContainer" in tableOptions({ index: "id" }, fakeRoot({})), false);
  } finally {
    delete globalThis.ShadowRoot;
  }
});

test("tableOptions: columns, index, luxon, and user options", () => {
  const built = tableOptions(
    { columns: [{ field: "px" }], options: { layout: "fitColumns", height: "50%", dependencies: { other: 1 } }, index: "symbol" },
    fakeRoot({}),
  );

  assert.deepEqual(Object.keys(built.dependencies), ["other", "luxon"]);
  assert.equal(typeof built.dependencies.luxon.DateTime.fromISO, "function");
  assert.deepEqual(
    { ...built, dependencies: undefined },
    { height: "50%", layout: "fitColumns", index: "symbol", columns: [{ field: "px" }], dependencies: undefined },
  );
});

test("tableOptions: no columns means automatic columns", () => {
  const built = tableOptions({ columns: [], options: {}, index: "id" }, fakeRoot({}));

  assert.equal(built.autoColumns, true);
  assert.equal("columns" in built, false);
});

for (const [name, autoColumns, rows, fields, expected] of [
  ["explicit columns", false, [{ id: 1, s: "x" }], [], false],
  ["first snapshot", true, [{ id: 1, s: "x" }], [], true],
  ["same fields", true, [{ id: 1, s: "x" }], ["id", "s"], false],
  ["new field", true, [{ id: 1, s: "x", px: 2 }], ["id", "s"], true],
  ["reordered fields", true, [{ s: "x", id: 1 }], ["id", "s"], true],
  ["no rows", true, [], ["id", "s"], false],
]) {
  test(`rebuildsColumns: ${name}`, () => {
    assert.equal(rebuildsColumns(autoColumns, rows, fields), expected);
  });
}
