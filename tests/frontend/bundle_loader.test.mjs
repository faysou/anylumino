import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import test from "node:test";

import { loaderSource } from "../../scripts/bundle-loader.mjs";

// The loader imports the bundle from a blob URL, which Node cannot import; a
// data URL of the same code stands in for it.
URL.createObjectURL = (blob) => blob.dataUrl;
URL.revokeObjectURL = () => {};
globalThis.Blob = class {
  constructor([code]) {
    this.dataUrl = `data:text/javascript,${encodeURIComponent(code)}`;
  }
};

function fakeModel(answer) {
  const handlers = new Set();
  const model = {
    sent: 0,
    handlers,
    on: (_event, callback) => handlers.add(callback),
    off: (_event, callback) => handlers.delete(callback),
    send: () => {
      model.sent += 1;
      if (answer !== undefined) {
        setTimeout(() => [...handlers].forEach((callback) => callback({ type: "anylumino-bundle", code: answer })), 0);
      }
    },
  };
  return model;
}

function fakeElement() {
  return {
    children: [],
    replaceChildren(...children) {
      this.children = children;
    },
  };
}

async function importLoader() {
  // A fresh outfile name gives each test its own globalThis key.
  const source = loaderSource(`${randomUUID()}.bundle.js`, "code", { timeoutMs: 50 });
  return (await import(`data:text/javascript,${encodeURIComponent(source)}`)).default;
}

test("a bundle request with no answer shows the failure and lets the next widget retry", async () => {
  globalThis.document = { createElement: () => ({ className: "", textContent: "" }) };
  const loader = await importLoader();
  const silent = fakeModel(undefined);
  const el = fakeElement();

  await loader.render({ model: silent, el });

  assert.equal(el.children.length, 1);
  assert.equal(el.children[0].className, "anylumino-LoadError");
  assert.match(el.children[0].textContent, /did not send the widget code within 0.05 s/);
  assert.equal(silent.handlers.size, 0);

  const live = fakeModel('export default { render: ({ el }) => el.replaceChildren("rendered") };');
  const retried = fakeElement();
  await loader.render({ model: live, el: retried });

  assert.equal(live.sent, 1);
  assert.deepEqual(retried.children, ["rendered"]);
  assert.equal(live.handlers.size, 0);
});

test("widgets waiting on one request share the module it loads", async () => {
  const loader = await importLoader();
  const first = fakeModel('export default { render: ({ el }) => el.replaceChildren("shared") };');
  const second = fakeModel(undefined);
  const elements = [fakeElement(), fakeElement()];

  await Promise.all([loader.render({ model: first, el: elements[0] }), loader.render({ model: second, el: elements[1] })]);

  assert.equal(first.sent + second.sent, 1);
  assert.deepEqual(elements.map((el) => el.children), [["shared"], ["shared"]]);
});
