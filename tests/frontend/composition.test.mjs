import assert from "node:assert/strict";
import test from "node:test";

import {
  clampIndex,
  coalesce,
  cssSize,
  installShortcutSuppression,
  modelListeners,
  observeResize,
  reusableSlots,
  titleFor,
  whenConnected,
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

function fakeElement(height, children = [], top = 0) {
  return {
    scrollHeight: height,
    offsetHeight: height,
    children,
    getBoundingClientRect: () => ({ top, bottom: top + height, width: height ? 300 : 0, height }),
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

  // Scrolled above the viewport, the wrapper's all-zero rect sits below the node's top.
  const scrolled = fakeElement(143, [fakeElement(0, [fakeElement(306, [], -65)])], -65);
  assert.equal(measuredContentHeight(scrolled, { includeSelf: false }), 306);
});


test("whenConnected resolves once the node joins the document or the signal aborts", async () => {
  const frames = [];
  const previous = { raf: globalThis.requestAnimationFrame, caf: globalThis.cancelAnimationFrame };
  globalThis.requestAnimationFrame = (callback) => frames.push(callback);
  globalThis.cancelAnimationFrame = () => {};
  try {
    assert.equal(await whenConnected({ isConnected: true }), true);

    const node = { isConnected: false };
    const pending = whenConnected(node);
    assert.equal(frames.length, 1);
    frames.shift()();
    assert.equal(frames.length, 1);
    node.isConnected = true;
    frames.shift()();
    assert.equal(await pending, true);
    assert.equal(frames.length, 0);

    const controller = new AbortController();
    const aborted = whenConnected({ isConnected: false }, controller.signal);
    controller.abort();
    assert.equal(await aborted, false);
    assert.equal(await whenConnected({ isConnected: false }, controller.signal), false);
  } finally {
    globalThis.requestAnimationFrame = previous.raf;
    globalThis.cancelAnimationFrame = previous.caf;
  }
});


function fakeNode() {
  const attributes = new Set();
  const listeners = new Map();
  return {
    attributes,
    listeners,
    hasAttribute: (name) => attributes.has(name),
    setAttribute: (name) => attributes.add(name),
    removeAttribute: (name) => attributes.delete(name),
    toggleAttribute: (name, force) => (force ? attributes.add(name) : attributes.delete(name)),
    addEventListener: (type, callback) => listeners.set(type, callback),
  };
}


test("installShortcutSuppression marks the root and the focused node while enabled", () => {
  const ATTRIBUTE = "data-lm-suppress-shortcuts";
  const root = fakeNode();
  const focused = fakeNode();
  const marked = fakeNode();
  marked.setAttribute(ATTRIBUTE);
  const values = { suppress_shortcuts: true };
  const model = { get: (name) => values[name] };

  const sync = installShortcutSuppression(model, root, new AbortController().signal);
  const rootMarked = root.hasAttribute(ATTRIBUTE);
  root.listeners.get("focusin")({ target: focused });
  const focusedMarked = focused.hasAttribute(ATTRIBUTE);
  root.listeners.get("focusout")({ target: focused });
  root.listeners.get("focusin")({ target: marked });
  root.listeners.get("focusout")({ target: marked });
  values.suppress_shortcuts = false;
  sync();
  root.listeners.get("focusin")({ target: focused });

  assert.equal(rootMarked, true);
  assert.equal(focusedMarked, true);
  assert.equal(focused.hasAttribute(ATTRIBUTE), false);
  assert.equal(marked.hasAttribute(ATTRIBUTE), true);
  assert.equal(root.hasAttribute(ATTRIBUTE), false);
});


test("observeResize calls back on each resize until the signal aborts", () => {
  const previous = globalThis.ResizeObserver;
  const observers = [];
  globalThis.ResizeObserver = class {
    constructor(callback) {
      this.callback = callback;
      this.observed = [];
      this.disconnected = false;
      observers.push(this);
    }
    observe(element) {
      this.observed.push(element);
    }
    disconnect() {
      this.disconnected = true;
    }
  };
  try {
    const controller = new AbortController();
    const element = { id: "root" };
    let calls = 0;
    observeResize(element, () => (calls += 1), controller.signal);
    observers[0].callback([]);
    observers[0].callback([]);
    controller.abort();

    assert.equal(observers.length, 1);
    assert.deepEqual(observers[0].observed, [element]);
    assert.equal(calls, 2);
    assert.equal(observers[0].disconnected, true);
  } finally {
    globalThis.ResizeObserver = previous;
  }
});
