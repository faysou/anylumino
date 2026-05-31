import { TabPanel, Widget } from "https://esm.sh/@lumino/widgets@2.8.0?bundle";
import {
  combineSignals,
  cssSize,
  disposeLuminoWidget,
  installResizeHandle,
  notifyLuminoWidgetVisible,
  removeModelListener,
  renderWidgetRef,
} from "./composition.js";

function clampIndex(index, length) {
  if (length <= 0) {
    return -1;
  }
  if (!Number.isFinite(index)) {
    return 0;
  }
  return Math.max(0, Math.min(length - 1, Math.trunc(index)));
}

function titleFor(index, titles) {
  const title = titles[index];
  if (typeof title === "string" && title.trim()) {
    return title;
  }
  return `Tab ${index + 1}`;
}

export default {
  initialize({ model }) {
    return {
      getCurrentIndex: () => model.get("selected_index"),
      getCurrentKey: () => {
        const keys = model.get("child_keys") ?? [];
        return keys[model.get("selected_index")] ?? null;
      },
      setCurrentIndex: (index) => {
        model.set("selected_index", index);
        model.save_changes();
      },
      setCurrentKey: (key) => {
        const index = (model.get("child_keys") ?? []).indexOf(key);
        if (index >= 0) {
          model.set("selected_index", index);
          model.save_changes();
        }
      },
    };
  },

  async render({ model, el, signal, host }) {
    if (!host?.getWidget) {
      throw new Error("[anylumino] The current anywidget host does not support widget composition.");
    }

    const root = document.createElement("div");
    root.className = "anylumino-TabPanelHost";
    root.style.width = cssSize(model.get("width"), "100%");
    root.style.height = cssSize(model.get("height"), "420px");
    el.replaceChildren(root);

    const panel = new TabPanel({ tabPlacement: model.get("tab_placement") || "top" });
    panel.addClass("anylumino-TabPanel");
    panel.tabsMovable = Boolean(model.get("tabs_movable"));
    Widget.attach(panel, root);

    let childController = new AbortController();
    let selectionFromFrontend = false;
    let syncingFromModel = false;

    const updatePanel = () => {
      panel.update();
    };

    const notifyCurrentWidgetVisible = () => {
      updatePanel();
      const currentWidget = panel.currentWidget;
      if (!currentWidget) {
        return;
      }

      notifyLuminoWidgetVisible(currentWidget, { dispatchWindowResize: true });
    };

    const syncSize = () => {
      root.style.width = cssSize(model.get("width"), "100%");
      root.style.height = cssSize(model.get("height"), "420px");
      notifyCurrentWidgetVisible();
    };

    installResizeHandle(model, root, notifyCurrentWidgetVisible, signal, { minHeight: 180 });

    const syncPlacement = () => {
      panel.tabPlacement = model.get("tab_placement") || "top";
      updatePanel();
    };

    const syncMovable = () => {
      panel.tabsMovable = Boolean(model.get("tabs_movable"));
    };

    const syncSelectedIndex = () => {
      if (selectionFromFrontend) {
        return;
      }
      const widgets = model.get("widgets") ?? [];
      try {
        syncingFromModel = true;
        panel.currentIndex = clampIndex(model.get("selected_index"), widgets.length);
      } finally {
        syncingFromModel = false;
      }
      notifyCurrentWidgetVisible();
    };

    const clearPanel = () => {
      childController.abort();
      childController = new AbortController();
      for (const widget of [...panel.widgets]) {
        disposeLuminoWidget(widget);
      }
    };

    const renderCurrentChild = async () => {
      const currentWidget = panel.currentWidget;
      if (!currentWidget || currentWidget.node.dataset.anyluminoRendered === "true") {
        notifyCurrentWidgetVisible();
        return;
      }
      if (currentWidget.node.dataset.anyluminoRendering === "true") {
        return;
      }

      currentWidget.node.dataset.anyluminoRendering = "true";
      await new Promise((resolve) => {
        requestAnimationFrame(() => requestAnimationFrame(resolve));
      });
      if (childController.signal.aborted || !currentWidget.isVisible) {
        currentWidget.node.dataset.anyluminoRendering = "false";
        return;
      }

      const ref = currentWidget.node.dataset.anyluminoRef;
      if (!ref) {
        currentWidget.node.dataset.anyluminoRendering = "false";
        return;
      }

      const childSignal = combineSignals(signal, childController.signal);
      if (childSignal.aborted || !currentWidget.isVisible) {
        currentWidget.node.dataset.anyluminoRendering = "false";
        return;
      }

      await renderWidgetRef(model, host, ref, currentWidget.node, childSignal);
      currentWidget.node.dataset.anyluminoRendered = "true";
      currentWidget.node.dataset.anyluminoRendering = "false";
      notifyCurrentWidgetVisible();
    };

    const renderChildren = async () => {
      const refs = model.get("widgets") ?? [];
      const titles = model.get("titles") ?? [];
      const keys = model.get("child_keys") ?? [];

      try {
        syncingFromModel = true;
        clearPanel();
        for (let index = 0; index < refs.length; index += 1) {
          const node = document.createElement("div");
          node.className = "anylumino-TabPanelChild";
          node.dataset.anyluminoRef = refs[index];
          node.dataset.anyluminoKey = keys[index] ?? "";
          node.dataset.anyluminoRendered = "false";
          node.dataset.anyluminoRendering = "false";
          const slot = new Widget({ node });
          slot.title.label = titleFor(index, titles);
          slot.title.caption = slot.title.label;
          panel.addWidget(slot);
        }
      } finally {
        syncingFromModel = false;
      }

      syncSelectedIndex();
      notifyCurrentWidgetVisible();
      await renderCurrentChild();
    };

    const onCurrentChanged = (_sender, args) => {
      const nextIndex = args.currentIndex;
      notifyCurrentWidgetVisible();
      void renderCurrentChild();
      if (syncingFromModel) {
        return;
      }
      if (model.get("selected_index") === nextIndex) {
        return;
      }
      selectionFromFrontend = true;
      try {
        model.set("selected_index", nextIndex);
        model.save_changes();
      } finally {
        selectionFromFrontend = false;
      }
    };

    const onWidgetsChanged = () => {
      void renderChildren();
    };

    const onTitlesChanged = () => {
      const titles = model.get("titles") ?? [];
      [...panel.widgets].forEach((widget, index) => {
        widget.title.label = titleFor(index, titles);
        widget.title.caption = widget.title.label;
      });
      updatePanel();
    };

    panel.currentChanged.connect(onCurrentChanged);
    window.addEventListener("resize", updatePanel, { signal });
    model.on("change:widgets", onWidgetsChanged);
    model.on("change:child_keys", onWidgetsChanged);
    model.on("change:titles", onTitlesChanged);
    model.on("change:selected_index", syncSelectedIndex);
    model.on("change:tab_placement", syncPlacement);
    model.on("change:tabs_movable", syncMovable);
    model.on("change:width", syncSize);
    model.on("change:height", syncSize);

    signal.addEventListener(
      "abort",
      () => {
        clearPanel();
        panel.currentChanged.disconnect(onCurrentChanged);
        removeModelListener(model, "change:widgets", onWidgetsChanged);
        removeModelListener(model, "change:child_keys", onWidgetsChanged);
        removeModelListener(model, "change:titles", onTitlesChanged);
        removeModelListener(model, "change:selected_index", syncSelectedIndex);
        removeModelListener(model, "change:tab_placement", syncPlacement);
        removeModelListener(model, "change:tabs_movable", syncMovable);
        removeModelListener(model, "change:width", syncSize);
        removeModelListener(model, "change:height", syncSize);
        panel.dispose();
        root.remove();
      },
      { once: true },
    );

    await renderChildren();
  },
};
