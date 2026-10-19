import { TabPanel, Widget } from "@lumino/widgets";
import {
  clampIndex,
  coalesce,
  combineSignals,
  cssSize,
  disposeLuminoWidget,
  fitContentEnabled,
  installResizeHandle,
  installShortcutSuppression,
  labelSlot,
  measuredContentHeight,
  modelListeners,
  notifyLuminoWidgetVisible,
  observeResize,
  renderChildError,
  renderWidgetRef,
  reusableSlots,
  whenConnected,
} from "./composition.js";

function createSlot(index, ref, titles, keys, parentSignal) {
  const node = document.createElement("div");
  node.className = "anylumino-TabPanelChild";
  node.dataset.anyluminoRef = ref;
  node.dataset.anyluminoRendered = "false";
  node.dataset.anyluminoRendering = "false";

  const slot = new Widget({ node });
  labelSlot(slot, index, titles, keys, "Tab");
  slot.anyluminoController = new AbortController();
  slot.anyluminoSignal = combineSignals(parentSignal, slot.anyluminoController.signal);
  return slot;
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
    const syncShortcuts = installShortcutSuppression(model, root, signal);
    root.style.width = cssSize(model.get("width"), "100%");
    root.style.height = cssSize(model.get("height"), "420px");
    root.classList.toggle("anylumino-mod-fitContent", fitContentEnabled(model));
    el.replaceChildren(root);

    const panel = new TabPanel({ tabPlacement: model.get("tab_placement") || "top" });
    panel.addClass("anylumino-TabPanel");
    panel.tabsMovable = Boolean(model.get("tabs_movable"));
    if (!(await whenConnected(root, signal))) {
      return;
    }
    Widget.attach(panel, root);

    let selectionFromFrontend = false;
    let syncingFromModel = false;
    let lastFitHeight = 0;

    const updatePanel = () => {
      panel.update();
      scheduleFitContent();
    };

    const fitContentNow = () => {
      if (!fitContentEnabled(model)) {
        return;
      }

      const currentWidget = panel.currentWidget;
      if (!currentWidget) {
        return;
      }

      // Everything around the current child: the tab bar and the panel borders and padding.
      const chrome = parseFloat(getComputedStyle(root).height) - currentWidget.node.getBoundingClientRect().height;
      const childHeight = measuredContentHeight(currentWidget.node, { includeSelf: false });
      const nextHeight = Math.max(180, Math.ceil(chrome + childHeight));
      if (!Number.isFinite(nextHeight) || Math.abs(nextHeight - lastFitHeight) < 2) {
        return;
      }

      lastFitHeight = nextHeight;
      root.style.height = `${nextHeight}px`;
      panel.update();
      notifyCurrentWidgetVisible();
    };

    let fitPending = false;
    const scheduleFitContent = () => {
      if (!fitContentEnabled(model) || fitPending) {
        return;
      }
      fitPending = true;
      requestAnimationFrame(() =>
        requestAnimationFrame(() => {
          fitPending = false;
          fitContentNow();
        }),
      );
    };

    // A callback can resize a child's content after it renders, so the fit follows the
    // current child's content boxes a few levels deep: an outer box that fills the slot
    // does not shrink with its content. display:contents mount roots have no box. Removed
    // nodes, such as a closing popup, change the measured height without resizing a box.
    const contentObserver = new ResizeObserver(scheduleFitContent);
    const mutationObserver = new MutationObserver(scheduleFitContent);
    signal.addEventListener(
      "abort",
      () => {
        contentObserver.disconnect();
        mutationObserver.disconnect();
      },
      { once: true },
    );
    const observeCurrentContent = () => {
      contentObserver.disconnect();
      mutationObserver.disconnect();
      const visit = (parent, depth) => {
        for (const child of parent.children) {
          const contents = getComputedStyle(child).display === "contents";
          if (!contents) {
            contentObserver.observe(child);
          }
          if (contents || depth > 1) {
            visit(child, contents ? depth : depth - 1);
          }
        }
      };
      if (fitContentEnabled(model) && panel.currentWidget) {
        visit(panel.currentWidget.node, 4);
        mutationObserver.observe(panel.currentWidget.node, { childList: true, subtree: true });
      }
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
      lastFitHeight = 0;
      root.classList.toggle("anylumino-mod-fitContent", fitContentEnabled(model));
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

    const renderCurrentChild = async () => {
      const slot = panel.currentWidget;
      if (!slot) {
        return;
      }
      if (slot.node.dataset.anyluminoRendered !== "false") {
        notifyCurrentWidgetVisible();
        return;
      }
      if (slot.node.dataset.anyluminoRendering === "true") {
        return;
      }

      slot.node.dataset.anyluminoRendering = "true";
      try {
        await new Promise((resolve) => {
          requestAnimationFrame(() => requestAnimationFrame(resolve));
        });
        if (slot.anyluminoSignal.aborted || !slot.isVisible) {
          return;
        }

        const ref = slot.node.dataset.anyluminoRef;
        if (!ref) {
          return;
        }

        await renderWidgetRef(model, host, ref, slot.node, slot.anyluminoSignal);
        slot.node.dataset.anyluminoRendered = "true";
        notifyCurrentWidgetVisible();
        observeCurrentContent();
        scheduleFitContent();
      } catch (error) {
        // Show the failure in the tab that owns it instead of leaving it blank.
        if (!slot.anyluminoSignal.aborted) {
          slot.node.dataset.anyluminoRendered = "error";
          renderChildError(slot.node, error);
          console.error("[anylumino] Child widget failed to render.", error);
        }
      } finally {
        slot.node.dataset.anyluminoRendering = "false";
      }
    };

    const panelMatchesModel = () => {
      const refs = model.get("widgets") ?? [];
      const slots = [...panel.widgets];
      return (
        slots.length === refs.length &&
        slots.every((slot, index) => slot.node.dataset.anyluminoRef === refs[index])
      );
    };

    const syncTitles = () => {
      const titles = model.get("titles") ?? [];
      const keys = model.get("child_keys") ?? [];
      [...panel.widgets].forEach((slot, index) => labelSlot(slot, index, titles, keys, "Tab"));
      updatePanel();
    };

    const renderChildren = async () => {
      // A tab drag already moved the tab, and Python echoes the new order back.
      // Rebuilding then would remount every child and snap the tabs back.
      if (panelMatchesModel()) {
        syncTitles();
        syncSelectedIndex();
        await renderCurrentChild();
        return;
      }

      const refs = model.get("widgets") ?? [];
      const titles = model.get("titles") ?? [];
      const keys = model.get("child_keys") ?? [];

      const reusable = reusableSlots([...panel.widgets]);
      const nextSlots = refs.map((ref, index) => {
        const existing = reusable.take(ref);
        if (existing === undefined) {
          return createSlot(index, ref, titles, keys, signal);
        }
        labelSlot(existing, index, titles, keys, "Tab");
        return existing;
      });

      for (const slot of reusable.rest()) {
        slot.anyluminoController.abort();
        disposeLuminoWidget(slot);
      }

      // Insert by index so a kept tab stays in the DOM: detaching a slot reloads any iframe
      // inside it and resets embedded state such as a chart.
      try {
        syncingFromModel = true;
        nextSlots.forEach((slot, index) => panel.insertWidget(index, slot));
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
      observeCurrentContent();
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

    // Lumino reorders its own tabs on a drag; Python has to learn the new order
    // or selected_key would point at the wrong child. The echoed widgets order
    // already matches the panel, so it does not cause a rebuild.
    const onTabMoved = (_sender, args) => {
      model.send({ type: "move", from: args.fromIndex, to: args.toIndex });
    };

    const rerender = coalesce(() => {
      if (!signal.aborted) {
        void renderChildren();
      }
    });

    panel.currentChanged.connect(onCurrentChanged);
    panel.tabBar.tabMoved.connect(onTabMoved);
    observeResize(root, updatePanel, signal);

    const unbind = modelListeners(model, [
      ["widgets", rerender],
      ["suppress_shortcuts", syncShortcuts],
      ["child_keys", rerender],
      ["titles", syncTitles],
      ["selected_index", syncSelectedIndex],
      ["tab_placement", syncPlacement],
      ["tabs_movable", syncMovable],
      [
        "fit_content",
        () => {
          syncSize();
          observeCurrentContent();
        },
      ],
      ["width", syncSize],
      ["height", syncSize],
    ]);

    signal.addEventListener(
      "abort",
      () => {
        for (const slot of [...panel.widgets]) {
          slot.anyluminoController.abort();
          disposeLuminoWidget(slot);
        }
        panel.currentChanged.disconnect(onCurrentChanged);
        panel.tabBar.tabMoved.disconnect(onTabMoved);
        unbind();
        disposeLuminoWidget(panel);
        root.remove();
      },
      { once: true },
    );

    await renderChildren();
  },
};
