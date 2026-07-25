import assert from "node:assert/strict";
import test from "node:test";

import {
  childSignature,
  modelProps,
  registeredComponent,
  resolveColorMode,
  sendModelAction,
  setModelOpen,
  toggleGroupValue,
} from "../../src/anylumino/static/astryx/astryx_bridge.mjs";


function fakeModel(props = {}) {
  const state = { props, is_open: false };
  const sent = [];
  return {
    state,
    sent,
    get: (name) => state[name],
    set: (name, value) => {
      state[name] = value;
    },
    save_changes: () => {
      state.saved = true;
    },
    send: (message) => sent.push(message),
  };
}


test("modelProps filters unsafe and component-reserved values only", () => {
  const model = fakeModel({
    children: "unsafe",
    ref: "unsafe",
    items: ["one"],
    density: "compact",
  });

  assert.deepEqual(modelProps(model), { items: ["one"], density: "compact" });
  assert.deepEqual(modelProps(model, ["items"]), { density: "compact" });
});


test("setModelOpen synchronizes state and preserves false transitions", () => {
  const model = fakeModel();

  setModelOpen(model, true);
  setModelOpen(model, false);

  assert.equal(model.state.is_open, false);
  assert.equal(model.state.saved, true);
  assert.deepEqual(model.sent, [
    { type: "open", is_open: true },
    { type: "open", is_open: false },
  ]);
});


test("sendModelAction preserves item values and named actions", () => {
  const model = fakeModel();

  sendModelAction(model, "export");
  sendModelAction(model, undefined, "confirm");

  assert.deepEqual(model.sent, [
    { type: "click", value: "export" },
    { type: "click", action: "confirm" },
  ]);
});


test("toggleGroupValue preserves the Astryx single and multiple value shapes", () => {
  assert.equal(toggleGroupValue("grid", false), "grid");
  assert.equal(toggleGroupValue(null, false), null);
  assert.deepEqual(toggleGroupValue(["bold", 7], true), ["bold", "7"]);
  assert.deepEqual(toggleGroupValue("bold", true), []);
});


test("registeredComponent rejects misspelled component names", () => {
  const Stack = () => null;

  assert.equal(registeredComponent({ Stack }, "Stack"), Stack);
  assert.throws(
    () => registeredComponent({ Stack }, "Stak"),
    /Unknown Astryx component "Stak"/,
  );
});


test("childSignature only changes when the composed children or layout change", () => {
  const model = fakeModel();
  model.set("component_name", "Stack");
  model.set("widgets", ["anywidget:one", "anywidget:two"]);
  model.set("child_keys", ["first", "second"]);
  const baseline = childSignature(model);

  model.set("value", "edited");
  assert.equal(childSignature(model), baseline);

  model.set("child_keys", ["first", "renamed"]);
  const renamed = childSignature(model);
  assert.notEqual(renamed, baseline);

  model.set("widgets", ["anywidget:two", "anywidget:one"]);
  const reordered = childSignature(model);
  assert.notEqual(reordered, renamed);

  model.set("component_name", "Toolbar");
  assert.notEqual(childSignature(model), reordered);
});


test("resolveColorMode maps the JupyterLab theme attribute onto Astryx modes", () => {
  const withLight = (value) => ({ body: { getAttribute: () => value } });

  assert.equal(resolveColorMode("dark", withLight("true")), "dark");
  assert.equal(resolveColorMode("system", withLight("false")), "system");
  assert.equal(resolveColorMode("jupyterlab", withLight("true")), "light");
  assert.equal(resolveColorMode("jupyterlab", withLight("false")), "dark");
  assert.equal(resolveColorMode("jupyterlab", withLight(null)), "system");
  assert.equal(resolveColorMode("jupyterlab", undefined), "system");
});
