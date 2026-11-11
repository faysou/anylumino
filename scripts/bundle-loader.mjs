import { createHash } from "node:crypto";
import { basename } from "node:path";

// How long a widget waits for Python to answer its bundle request.
export const BUNDLE_TIMEOUT_MS = 10_000;

// anywidget imports a widget's `_esm` as its own module for every widget model,
// so each widget would hold its own copy of the bundle and its libraries. The
// widgets load a small loader instead: the first one on a page asks Python for
// the bundle with an `anylumino-bundle` message (`SharedBundleWidget`) and
// imports it once, and the module is kept on `globalThis` under a key that
// changes with the bundle content, so every later widget reuses it. A request
// that fails or gets no answer in time clears the key, so the next widget asks
// again, and every widget waiting on it shows the failure.
export function loaderSource(outfile, code, { timeoutMs = BUNDLE_TIMEOUT_MS } = {}) {
  const hash = createHash("sha256").update(code).digest("hex").slice(0, 16);
  const key = JSON.stringify(`anylumino:${basename(outfile)}:${hash}`);
  return `const key = Symbol.for(${key});

function load(model) {
  globalThis[key] ??= new Promise((resolve, reject) => {
    const stopListening = () => {
      try {
        model.off("msg:custom", onMessage);
      } catch {
        model.off("msg:custom", onMessage, null);
      }
    };
    const timer = setTimeout(() => {
      stopListening();
      reject(new Error("the kernel did not send the widget code within ${timeoutMs / 1000} s"));
    }, ${timeoutMs});
    const onMessage = (content) => {
      if (content?.type !== "anylumino-bundle") {
        return;
      }
      clearTimeout(timer);
      stopListening();
      const url = URL.createObjectURL(new Blob([content.code], { type: "text/javascript" }));
      import(url).then((module) => resolve(module.default), reject).finally(() => URL.revokeObjectURL(url));
    };
    model.on("msg:custom", onMessage);
    model.send({ type: "anylumino-bundle" });
  }).catch((error) => {
    delete globalThis[key];
    throw error;
  });
  return globalThis[key];
}

function showLoadError(el, error) {
  const message = document.createElement("div");
  message.className = "anylumino-LoadError";
  message.textContent = \`[anylumino] The widget failed to load: \${String(error?.message ?? error)}. Rerun the cell to retry.\`;
  el.replaceChildren(message);
}

// anywidget fails a model whose initialize takes over two seconds, so initialize
// only starts the request and render waits for the bundle.
export default {
  initialize({ model }) {
    load(model).catch(() => {});
  },
  async render(context) {
    let module;
    try {
      module = await load(context.model);
    } catch (error) {
      showLoadError(context.el, error);
      return;
    }
    return module.render(context);
  },
};
`;
}
