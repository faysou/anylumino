import assert from "node:assert/strict";
import test from "node:test";

import {
  clampIndex,
  coalesce,
  cssSize,
  modelListeners,
  reusableSlots,
  titleFor,
} from "../../src/anylumino/static/layout/composition.js";


function fakeModel() {
  const handlers = new Map();
  return {
    handlers,
    on: (event, callback) => {
      handlers.set(event, [...(handlers.get(event) ?? []), callback]);
    },
    off: (event, callback) => {
      handlers.set(event, (handlers.get(event) ?? []).filter((entry) => entry !== callback));
    },
    emit: (event) => {
      for (const callback of handlers.get(event) ?? []) {
        callback();
      }
    },
  };
}


test("cssSize keeps explicit sizes and falls back for blanks", () => {
  assert.equal(cssSize("240px", "100%"), "240px");
  assert.equal(cssSize("   ", "100%"), "100%");
  assert.equal(cssSize(undefined, "420px"), "420px");
  assert.equal(cssSize(240, "100%"), "100%");
});


test("clampIndex stays inside the child range", () => {
  assert.equal(clampIndex(0, 0), -1);
  assert.equal(clampIndex(-3, 4), 0);
  assert.equal(clampIndex(7, 4), 3);
  assert.equal(clampIndex(2.7, 4), 2);
  assert.equal(clampIndex(Number.NaN, 4), 0);
});


test("titleFor uses the label, then the family prefix", () => {
  assert.equal(titleFor(0, ["Orders"], "Tab"), "Orders");
  assert.equal(titleFor(1, ["Orders", "  "], "Tab"), "Tab 2");
  assert.equal(titleFor(2, ["Orders"], "Widget"), "Widget 3");
});


test("coalesce collapses a burst of trait changes into one pass", async () => {
  let calls = 0;
  const run = coalesce(() => {
    calls += 1;
  });

  run();
  run();
  run();
  assert.equal(calls, 0);

  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.equal(calls, 1);

  run();
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.equal(calls, 2);
});


test("modelListeners binds and unbinds a listener set as one unit", () => {
  const model = fakeModel();
  const seen = [];
  const onWidgets = () => seen.push("widgets");
  const onWidth = () => seen.push("width");

  const unbind = modelListeners(model, [
    ["widgets", onWidgets],
    ["width", onWidth],
  ]);

  model.emit("change:widgets");
  model.emit("change:width");
  unbind();
  model.emit("change:widgets");
  model.emit("change:width");

  assert.deepEqual(seen, ["widgets", "width"]);
});


test("reusableSlots hands back one slot per ref and reports the rest", () => {
  const slot = (ref) => ({ ref, node: { dataset: { anyluminoRef: ref } } });
  const first = slot("anywidget:one");
  const second = slot("anywidget:two");
  const duplicate = slot("anywidget:one");

  const reusable = reusableSlots([first, second, duplicate]);

  assert.equal(reusable.take("anywidget:one"), first);
  assert.equal(reusable.take("anywidget:one"), duplicate);
  assert.equal(reusable.take("anywidget:one"), undefined);
  assert.equal(reusable.take("anywidget:missing"), undefined);
  assert.deepEqual(reusable.rest(), [second]);
});

function fakeElement(height, children = []) {
  return {
    scrollHeight: height,
    offsetHeight: height,
    children,
    getBoundingClientRect: () => ({ top: 0, bottom: height, height }),
  };
}

test("measuredContentHeight measures through zero-box wrappers", async () => {
  const { measuredContentHeight } = await import("../../src/anylumino/static/layout/composition.js");
  const plain = fakeElement(0, [fakeElement(120)]);
  assert.equal(measuredContentHeight(plain, { includeSelf: false }), 120);

  const wrapped = fakeElement(0, [fakeElement(0, [fakeElement(56), fakeElement(32)])]);
  assert.equal(measuredContentHeight(wrapped, { includeSelf: false }), 56);

  const empty = fakeElement(0, [fakeElement(0, [])]);
  assert.equal(measuredContentHeight(empty, { includeSelf: false }), 0);
});
