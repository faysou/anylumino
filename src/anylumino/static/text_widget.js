export default {
  initialize({ model }) {
    return {
      getText: () => model.get("text"),
    };
  },

  render({ model, el, signal }) {
    const node = document.createElement("div");
    node.className = "anylumino-TextWidget";

    const syncText = () => {
      node.textContent = model.get("text");
    };

    syncText();
    model.on("change:text", syncText);
    signal.addEventListener("abort", () => model.off("change:text", syncText));
    el.replaceChildren(node);
  },
};
