import {
  AccordionPanel,
  BoxPanel,
  DockPanel,
  Panel,
  SplitPanel,
  StackedPanel,
  Widget,
} from "@lumino/widgets";
import {
  clampIndex,
  coalesce,
  combineSignals,
  cssSize,
  disposeLuminoWidget,
  fitContentEnabled,
  installResizeHandle,
  labelSlot,
  measuredContentHeight,
  modelListeners,
  notifyLuminoWidgetVisible,
  renderChildError,
  renderWidgetRef,
  reusableSlots,
  whenConnected,
} from "./composition.js";

function slotIsVisible(slot) {
  if (!slot || slot.isHidden) {
    return false;
  }
  return slot.node.isConnected;
}

function notifySlotVisible(slot) {
  notifyLuminoWidgetVisible(slot);
}

function syncScroll(root, viewport, slots, model) {
  const scrollX = Boolean(model.get("scroll_x"));
  const scrollY = Boolean(model.get("scroll_y"));
  root.classList.toggle("anylumino-mod-scrollX", scrollX);
  root.classList.toggle("anylumino-mod-scrollY", scrollY);
  viewport.style.overflowX = scrollX ? "auto" : "hidden";
  viewport.style.overflowY = scrollY ? "auto" : "hidden";

  const childMinWidth = cssSize(model.get("child_min_width"), "0px");
  const childMinHeight = cssSize(model.get("child_min_height"), "0px");
  for (const slot of slots) {
    slot.node.style.minWidth = childMinWidth;
    slot.node.style.minHeight = childMinHeight;
  }
}

function measureSlotHeight(slot) {
  return measuredContentHeight(slot?.node, { includeSelf: false });
}

function createSlot(index, ref, titles, keys, model, parentSignal) {
  const node = document.createElement("div");
  node.className = "anylumino-LayoutChild";
  node.dataset.anyluminoRef = ref;
  node.dataset.anyluminoRendered = "false";
  node.dataset.anyluminoRendering = "false";
  node.style.minWidth = cssSize(model.get("child_min_width"), "0px");
  node.style.minHeight = cssSize(model.get("child_min_height"), "0px");

  const slot = new Widget({ node });
  labelSlot(slot, index, titles, keys, "Widget");
  // Each child owns its abort signal so rebuilding the panel only tears down
  // the children that actually left.
  slot.anyluminoController = new AbortController();
  slot.anyluminoSignal = combineSignals(parentSignal, slot.anyluminoController.signal);
  return slot;
}

function reuseSlot(slot, index, titles, keys) {
  slot.parent = null;
  labelSlot(slot, index, titles, keys, "Widget");
  return slot;
}

function createPanel(model, root, slots, onSplitSizesChanged) {
  const kind = model.get("layout_kind");

  if (kind === "box" || kind === "responsive") {
    const direction =
      kind === "responsive"
        ? model.get("wide_direction") || "left-to-right"
        : model.get("direction") || "left-to-right";
    if (kind === "box" && (model.get("scroll_x") || model.get("scroll_y"))) {
      const panel = new Panel();
      panel.addClass("anylumino-box");
      panel.addClass("anylumino-scrollBox");
      panel.addClass(`anylumino-scrollBox-${direction}`);
      panel.node.style.gap = cssSize(model.get("spacing"), "8px");
      slots.forEach((slot) => panel.addWidget(slot));
      return panel;
    }

    const panel = new BoxPanel({ direction, spacing: Number(model.get("spacing") ?? 8) });
    panel.addClass(`anylumino-${kind}`);

    const stretches = model.get("stretches") ?? [];
    slots.forEach((slot, index) => {
      panel.addWidget(slot);
      BoxPanel.setStretch(slot, Number(stretches[index] ?? 0));
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
    slots.forEach((slot) => panel.addWidget(slot));
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

    // Scrolling happens inside the viewport so the resize handle, which is
    // positioned against the host, stays put instead of scrolling away.
    const viewport = document.createElement("div");
    viewport.className = "anylumino-LayoutViewport";
    root.appendChild(viewport);

    let panel = null;
    let slots = [];
    let splitSizesFromFrontend = false;
    let lastFitHeight = 0;

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
      scheduleFitContent();
    };

    const syncSize = () => {
      root.style.width = cssSize(model.get("width"), "100%");
      root.style.height = cssSize(model.get("height"), "420px");
      if (!fitContentEnabled(model)) {
        lastFitHeight = 0;
      }
      root.classList.toggle("anylumino-mod-fitContent", fitContentEnabled(model));
      syncScroll(root, viewport, slots, model);
      notifyResize();
    };

    const fitContentNow = () => {
      if (!fitContentEnabled(model) || !panel || slots.length === 0) {
        return;
      }

      const kind = model.get("layout_kind");
      const visibleSlots = slots.filter(slotIsVisible);
      if (visibleSlots.length === 0) {
        return;
      }

      for (const slot of visibleSlots) {
        const height = measureSlotHeight(slot);
        if (height > 0) {
          slot.node.style.minHeight = `${height}px`;
        }
      }
      panel.update();

      requestAnimationFrame(() => {
        let nextHeight = measuredContentHeight(panel.node);
        if (kind === "box" || kind === "responsive") {
          const direction = panel.direction || model.get("direction") || "top-to-bottom";
          const horizontal = direction === "left-to-right" || direction === "right-to-left";
          const spacing = Number(model.get("spacing") ?? 8);
          const childHeights = visibleSlots.map(measureSlotHeight).filter((height) => height > 0);
          if (childHeights.length > 0) {
            nextHeight = horizontal
              ? Math.max(...childHeights)
              : childHeights.reduce((total, height) => total + height, 0) + spacing * Math.max(0, childHeights.length - 1);
          }
        } else if (kind === "stacked") {
          const selected = visibleSlots.find((slot) => !slot.isHidden) ?? visibleSlots[0];
          nextHeight = measureSlotHeight(selected);
        }

        nextHeight = Math.max(160, Math.ceil(nextHeight));
        // Compare against the rendered height too: syncSize can reset the root
        // to the model height after a fit, which makes the cache stale.
        const renderedHeight = root.getBoundingClientRect().height;
        if (
          !Number.isFinite(nextHeight)
          || (Math.abs(nextHeight - lastFitHeight) < 2 && Math.abs(nextHeight - renderedHeight) < 2)
        ) {
          return;
        }
        lastFitHeight = nextHeight;
        root.style.height = `${nextHeight}px`;
        panel.update();
        for (const slot of visibleSlots) {
          notifySlotVisible(slot);
        }
      });
    };

    const scheduleFitContent = () => {
      if (!fitContentEnabled(model)) {
        return;
      }
      requestAnimationFrame(() => requestAnimationFrame(fitContentNow));
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

    installResizeHandle(model, root, notifyResize, signal);

    const renderChild = async (slot) => {
      if (slot.node.dataset.anyluminoRendered !== "false") {
        notifySlotVisible(slot);
        return;
      }
      if (slot.node.dataset.anyluminoRendering === "true" || !slotIsVisible(slot)) {
        return;
      }

      slot.node.dataset.anyluminoRendering = "true";
      try {
        await new Promise((resolve) => {
          requestAnimationFrame(() => requestAnimationFrame(resolve));
        });
        if (slot.anyluminoSignal.aborted || !slotIsVisible(slot)) {
          return;
        }

        await renderWidgetRef(model, host, slot.node.dataset.anyluminoRef, slot.node, slot.anyluminoSignal);
        slot.node.dataset.anyluminoRendered = "true";
        notifySlotVisible(slot);
        scheduleFitContent();
      } catch (error) {
        // Children render one after another, so a throw here would otherwise
        // leave every later sibling blank with no explanation.
        if (!slot.anyluminoSignal.aborted) {
          slot.node.dataset.anyluminoRendered = "error";
          renderChildError(slot.node, error);
          console.error("[anylumino] Child widget failed to render.", error);
        }
      } finally {
        slot.node.dataset.anyluminoRendering = "false";
      }
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

    const syncTitles = () => {
      const titles = model.get("titles") ?? [];
      const keys = model.get("child_keys") ?? [];
      slots.forEach((slot, index) => labelSlot(slot, index, titles, keys, "Widget"));
      panel?.update();
    };

    const disposeSlots = (targets) => {
      for (const slot of targets) {
        slot.anyluminoController.abort();
        disposeLuminoWidget(slot);
      }
    };

    const renderPanel = async () => {
      const refs = model.get("widgets") ?? [];
      const titles = model.get("titles") ?? [];
      const keys = model.get("child_keys") ?? [];

      // Reuse the slot of any child that is still composed, so adding a sibling
      // or renaming a section does not remount every iframe and plot.
      const reusable = reusableSlots(slots);
      const nextSlots = refs.map((ref, index) => {
        const existing = reusable.take(ref);
        return existing === undefined
          ? createSlot(index, ref, titles, keys, model, signal)
          : reuseSlot(existing, index, titles, keys);
      });

      disposeSlots(reusable.rest());
      if (panel) {
        disposeLuminoWidget(panel);
      }
      viewport.replaceChildren();
      slots = nextSlots;

      syncScroll(root, viewport, slots, model);
      panel = createPanel(model, root, slots, saveSplitSizes);
      if (!(await whenConnected(viewport, signal))) {
        return;
      }
      Widget.attach(panel, viewport);
      root.classList.toggle("anylumino-mod-fitContent", fitContentEnabled(model));
      syncStackedIndex();
      panel.update();
      await renderVisibleChildren();
      scheduleFitContent();
    };

    const rerender = coalesce(() => {
      if (!signal.aborted) {
        void renderPanel();
      }
    });

    root.addEventListener("click", () => setTimeout(() => void renderVisibleChildren(), 0), { signal });
    window.addEventListener("resize", syncSize, { signal });

    const unbind = modelListeners(model, [
      ["widgets", rerender],
      ["child_keys", rerender],
      ["layout_kind", rerender],
      ["direction", rerender],
      ["orientation", rerender],
      ["spacing", rerender],
      ["stretches", rerender],
      ["mode", rerender],
      ["columns", rerender],
      ["rows", rerender],
      ["gap", rerender],
      ["areas", rerender],
      ["breakpoint", rerender],
      ["wide_direction", rerender],
      ["narrow_direction", rerender],
      ["titles", syncTitles],
      ["sizes", syncSplitSizesFromModel],
      ["scroll_x", syncSize],
      ["scroll_y", syncSize],
      ["child_min_width", syncSize],
      ["child_min_height", syncSize],
      ["fit_content", syncSize],
      ["selected_index", syncStackedIndex],
      ["width", syncSize],
      ["height", syncSize],
    ]);

    signal.addEventListener(
      "abort",
      () => {
        disposeSlots(slots);
        slots = [];
        if (panel) {
          disposeLuminoWidget(panel);
          panel = null;
        }
        unbind();
        root.remove();
      },
      { once: true },
    );

    await renderPanel();
  },
};
