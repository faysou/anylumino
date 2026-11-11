const key = Symbol.for("anylumino:astryx_widget.bundle.js:476b7a270abf745a");

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
      reject(new Error("the kernel did not send the widget code within 10 s"));
    }, 10000);
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
  message.textContent = `[anylumino] The widget failed to load: ${String(error?.message ?? error)}. Rerun the cell to retry.`;
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
