import {
  AccordionPanel,
  BoxPanel,
  DockPanel,
  Panel,
  SplitPanel,
  StackedPanel,
  Widget,
} from "https://esm.sh/@lumino/widgets@2.8.0?bundle";
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
  return `Widget ${index + 1}`;
}

function slotIsVisible(slot) {
  if (!slot || slot.isHidden) {
    return false;
  }
  return document.body.contains(slot.node);
}

function notifySlotVisible(slot) {
  notifyLuminoWidgetVisible(slot);
}

function syncScroll(root, slots, model) {
  const scrollX = Boolean(model.get("scroll_x"));
  const scrollY = Boolean(model.get("scroll_y"));
  root.classList.toggle("anylumino-mod-scrollX", scrollX);
  root.classList.toggle("anylumino-mod-scrollY", scrollY);
  root.style.overflowX = scrollX ? "auto" : "hidden";
  root.style.overflowY = scrollY ? "auto" : "hidden";

  const childMinWidth = cssSize(model.get("child_min_width"), "0px");
  const childMinHeight = cssSize(model.get("child_min_height"), "0px");
  for (const slot of slots) {
    slot.node.style.minWidth = childMinWidth;
    slot.node.style.minHeight = childMinHeight;
  }
}

function createSlot(index, ref, titles, keys, model) {
  const node = document.createElement("div");
  node.className = "anylumino-LayoutChild";
  node.dataset.anyluminoRef = ref;
  node.dataset.anyluminoKey = keys[index] ?? "";
  node.dataset.anyluminoRendered = "false";
  node.dataset.anyluminoRendering = "false";
  node.style.minWidth = cssSize(model.get("child_min_width"), "0px");
  node.style.minHeight = cssSize(model.get("child_min_height"), "0px");

  const slot = new Widget({ node });
  slot.title.label = titleFor(index, titles);
  slot.title.caption = slot.title.label;
  return slot;
}

function createPanel(model, root, slots, onSplitSizesChanged) {
  const kind = model.get("layout_kind");
  const titles = model.get("titles") ?? [];

  if (kind === "box" || kind === "responsive") {
    const direction =
      kind === "responsive"
        ? model.get("wide_direction") || "left-to-right"
        : model.get("direction") || "left-to-right";
    const panel = new BoxPanel({ direction, spacing: Number(model.get("spacing") ?? 8) });
    panel.addClass(`anylumino-${kind}`);

    const stretches = model.get("stretches") ?? [];
    slots.forEach((slot, index) => {
      panel.addWidget(slot);
      BoxPanel.setStretch(slot, Number(stretches[index] ?? 1));
    });

    if (kind === "responsive") {
      const syncDirection = () => {
        const breakpoint = Number(model.get("breakpoint") ?? 760);
        panel.direction =
          root.getBoundingClientRect().width < breakpoint
            ? model.get("narrow_direction") || "top-to-bottom"
            : model.get("wide_direction") || "left-to-right";
        panel.spacing = Number(model.get("spacing") ?? 8);
        panel.update();
      };
      const observer = new ResizeObserver(syncDirection);
      observer.observe(root);
      panel.disposed.connect(() => observer.disconnect());
      syncDirection();
    }
    return panel;
  }

  if (kind === "split") {
    const panel = new SplitPanel({
      orientation: model.get("orientation") || "horizontal",
      spacing: Number(model.get("spacing") ?? 6),
    });
    panel.addClass("anylumino-split");
    slots.forEach((slot) => panel.addWidget(slot));
    requestAnimationFrame(() => {
      const sizes = model.get("sizes") ?? [];
      if (sizes.length > 0 && typeof panel.setRelativeSizes === "function") {
        panel.setRelativeSizes(sizes.map(Number));
      }
    });
    const syncSizes = () => {
      if (typeof panel.relativeSizes === "function") {
        onSplitSizesChanged?.(panel.relativeSizes().map(Number));
      }
    };
    panel.handleMoved.connect(syncSizes);
    panel.disposed.connect(() => panel.handleMoved.disconnect(syncSizes));
    return panel;
  }

  if (kind === "dock") {
    const panel = new DockPanel();
    panel.addClass("anylumino-dock");
    let ref = null;
    slots.forEach((slot, index) => {
      if (index === 0) {
        panel.addWidget(slot);
      } else {
        panel.addWidget(slot, { mode: model.get("mode") || "split-right", ref });
      }
      ref = slot;
    });
    return panel;
  }

  if (kind === "accordion") {
    const panel = new AccordionPanel();
    panel.addClass("anylumino-accordion");
    slots.forEach((slot, index) => {
      slot.title.label = titleFor(index, titles);
      panel.addWidget(slot);
    });
    return panel;
  }

  if (kind === "stacked") {
    const panel = new StackedPanel();
    panel.addClass("anylumino-stacked");
    slots.forEach((slot) => panel.addWidget(slot));
    return panel;
  }

  if (kind === "grid") {
    const panel = new Panel();
    panel.addClass("anylumino-grid");
    panel.node.style.gridTemplateColumns = model.get("columns") || "1fr 1fr";
    panel.node.style.gridTemplateRows = model.get("rows") || "auto";
    panel.node.style.gap = cssSize(model.get("gap"), "8px");
    const areas = model.get("areas") ?? [];
    slots.forEach((slot, index) => {
      const area = areas[index] ?? {};
      if (area.column) {
        slot.node.style.gridColumn = area.column;
      }
      if (area.row) {
        slot.node.style.gridRow = area.row;
      }
      panel.addWidget(slot);
    });
    return panel;
  }

  return new Panel();
}

export default {
  initialize({ model }) {
    return {
      getLayoutKind: () => model.get("layout_kind"),
    };
  },

  async render({ model, el, signal, host }) {
    if (!host?.getWidget) {
      throw new Error("[anylumino] The current anywidget host does not support widget composition.");
    }

    const root = document.createElement("div");
    root.className = `anylumino-LayoutHost anylumino-${model.get("layout_kind")}Host`;
    root.style.width = cssSize(model.get("width"), "100%");
    root.style.height = cssSize(model.get("height"), "420px");
    el.replaceChildren(root);

    let panel = null;
    let slots = [];
    let childController = new AbortController();
    let splitSizesFromFrontend = false;

    const saveSplitSizes = (sizes) => {
      if (!Array.isArray(sizes) || sizes.length === 0) {
        return;
      }
      splitSizesFromFrontend = true;
      model.set("sizes", sizes);
      model.save_changes();
      queueMicrotask(() => {
        splitSizesFromFrontend = false;
      });
    };

    const notifyResize = () => {
      if (panel) {
        panel.update();
      }
      void renderVisibleChildren();
    };

    const syncSize = () => {
      root.style.width = cssSize(model.get("width"), "100%");
      root.style.height = cssSize(model.get("height"), "420px");
      syncScroll(root, slots, model);
      notifyResize();
    };

    const syncSplitSizesFromModel = () => {
      if (splitSizesFromFrontend) {
        return;
      }
      if (model.get("layout_kind") !== "split") {
        return;
      }
      const sizes = model.get("sizes") ?? [];
      if (panel && sizes.length > 0 && typeof panel.setRelativeSizes === "function") {
        panel.setRelativeSizes(sizes.map(Number));
        notifyResize();
      }
    };

    const resizeHandle = installResizeHandle(model, root, notifyResize, signal);

    const renderChild = async (slot) => {
      if (slot.node.dataset.anyluminoRendered === "true") {
        notifySlotVisible(slot);
        return;
      }
      if (slot.node.dataset.anyluminoRendering === "true") {
        return;
      }
      if (!slotIsVisible(slot)) {
        return;
      }

      slot.node.dataset.anyluminoRendering = "true";
      await new Promise((resolve) => {
        requestAnimationFrame(() => requestAnimationFrame(resolve));
      });
      if (childController.signal.aborted || !slotIsVisible(slot)) {
        slot.node.dataset.anyluminoRendering = "false";
        return;
      }

      const ref = slot.node.dataset.anyluminoRef;
      const childSignal = combineSignals(signal, childController.signal);
      if (childSignal.aborted || !slotIsVisible(slot)) {
        slot.node.dataset.anyluminoRendering = "false";
        return;
      }

      await renderWidgetRef(model, host, ref, slot.node, childSignal);
      slot.node.dataset.anyluminoRendered = "true";
      slot.node.dataset.anyluminoRendering = "false";
      notifySlotVisible(slot);
    };

    const renderVisibleChildren = async () => {
      for (const slot of slots) {
        if (slotIsVisible(slot)) {
          await renderChild(slot);
        }
      }
    };

    const syncStackedIndex = () => {
      if (model.get("layout_kind") !== "stacked") {
        return;
      }
      const selectedIndex = clampIndex(model.get("selected_index"), slots.length);
      slots.forEach((slot, index) => {
        if (index === selectedIndex) {
          slot.show();
        } else {
          slot.hide();
        }
      });
      panel?.update();
      void renderVisibleChildren();
    };

    const clearPanel = () => {
      childController.abort();
      childController = new AbortController();
      if (panel) {
        disposeLuminoWidget(panel);
      }
      slots = [];
      root.replaceChildren(resizeHandle);
      panel = null;
    };

    const renderPanel = async () => {
      clearPanel();
      const refs = model.get("widgets") ?? [];
      const titles = model.get("titles") ?? [];
      const keys = model.get("child_keys") ?? [];
      slots = refs.map((ref, index) => createSlot(index, ref, titles, keys, model));
      syncScroll(root, slots, model);
      panel = createPanel(model, root, slots, saveSplitSizes);
      Widget.attach(panel, root);
      syncStackedIndex();
      panel.update();
      await renderVisibleChildren();
    };

    const rerender = () => {
      void renderPanel();
    };

    root.addEventListener("click", () => setTimeout(() => void renderVisibleChildren(), 0), { signal });
    window.addEventListener("resize", syncSize, { signal });
    model.on("change:widgets", rerender);
    model.on("change:child_keys", rerender);
    model.on("change:titles", rerender);
    model.on("change:layout_kind", rerender);
    model.on("change:direction", rerender);
    model.on("change:orientation", rerender);
    model.on("change:spacing", rerender);
    model.on("change:stretches", rerender);
    model.on("change:sizes", syncSplitSizesFromModel);
    model.on("change:mode", rerender);
    model.on("change:columns", rerender);
    model.on("change:rows", rerender);
    model.on("change:gap", rerender);
    model.on("change:areas", rerender);
    model.on("change:breakpoint", rerender);
    model.on("change:wide_direction", rerender);
    model.on("change:narrow_direction", rerender);
    model.on("change:scroll_x", syncSize);
    model.on("change:scroll_y", syncSize);
    model.on("change:child_min_width", syncSize);
    model.on("change:child_min_height", syncSize);
    model.on("change:selected_index", syncStackedIndex);
    model.on("change:width", syncSize);
    model.on("change:height", syncSize);

    signal.addEventListener(
      "abort",
      () => {
        clearPanel();
        removeModelListener(model, "change:widgets", rerender);
        removeModelListener(model, "change:child_keys", rerender);
        removeModelListener(model, "change:titles", rerender);
        removeModelListener(model, "change:layout_kind", rerender);
        removeModelListener(model, "change:direction", rerender);
        removeModelListener(model, "change:orientation", rerender);
        removeModelListener(model, "change:spacing", rerender);
        removeModelListener(model, "change:stretches", rerender);
        removeModelListener(model, "change:sizes", syncSplitSizesFromModel);
        removeModelListener(model, "change:mode", rerender);
        removeModelListener(model, "change:columns", rerender);
        removeModelListener(model, "change:rows", rerender);
        removeModelListener(model, "change:gap", rerender);
        removeModelListener(model, "change:areas", rerender);
        removeModelListener(model, "change:breakpoint", rerender);
        removeModelListener(model, "change:wide_direction", rerender);
        removeModelListener(model, "change:narrow_direction", rerender);
        removeModelListener(model, "change:scroll_x", syncSize);
        removeModelListener(model, "change:scroll_y", syncSize);
        removeModelListener(model, "change:child_min_width", syncSize);
        removeModelListener(model, "change:child_min_height", syncSize);
        removeModelListener(model, "change:selected_index", syncStackedIndex);
        removeModelListener(model, "change:width", syncSize);
        removeModelListener(model, "change:height", syncSize);
        root.remove();
      },
      { once: true },
    );

    await renderPanel();
  },
};
