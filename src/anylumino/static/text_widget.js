export default {
  initialize({ model }) {
    return {
      getValue: () => model.get("value"),
    };
  },

  render({ model, el, signal }) {
    const node = document.createElement("div");
    node.className = "anylumino-TextWidget";

    const syncValue = () => {
      node.textContent = model.get("value");
    };

    syncValue();
    model.on("change:value", syncValue);
    signal.addEventListener("abort", () => model.off("change:value", syncValue));
    el.replaceChildren(node);
  },
};
