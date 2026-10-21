const key = Symbol.for("anylumino:tab_panel.bundle.js:08c467687c5b823f");

function load(model) {
  globalThis[key] ??= new Promise((resolve, reject) => {
    const onMessage = (content) => {
      if (content?.type !== "anylumino-bundle") {
        return;
      }
      try {
        model.off("msg:custom", onMessage);
      } catch {
        model.off("msg:custom", onMessage, null);
      }
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

// anywidget fails a model whose initialize takes over two seconds, so initialize
// only starts the request and render waits for the bundle.
export default {
  initialize({ model }) {
    load(model).catch(() => {});
  },
  async render(context) {
    return (await load(context.model)).render(context);
  },
};
