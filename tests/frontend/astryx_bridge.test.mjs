import assert from "node:assert/strict";
import test from "node:test";

import {
  modelProps,
  registeredComponent,
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
