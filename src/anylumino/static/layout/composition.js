function modelIdFromRef(ref) {
  if (typeof ref === "string" && ref.startsWith("anywidget:")) {
    return ref.slice("anywidget:".length);
  }
  return ref;
}

function isMissingAnywidgetBinding(error) {
  return String(error?.message ?? error).includes("No binding found for widget");
}

export function cssSize(value, fallback) {
  if (typeof value === "string" && value.trim()) {
    return value;
  }
  return fallback;
}

export function clampIndex(index, length) {
  if (length <= 0) {
    return -1;
  }
  if (!Number.isFinite(index)) {
    return 0;
  }
  return Math.max(0, Math.min(length - 1, Math.trunc(index)));
}

export function titleFor(index, titles, prefix) {
  const title = titles[index];
  if (typeof title === "string" && title.trim()) {
    return title;
  }
  return `${prefix} ${index + 1}`;
}

export function fitContentEnabled(model) {
  return Boolean(model.get("fit_content"));
}

/**
 * Point a child slot at the key and title it holds at `index`.
 */
export function labelSlot(slot, index, titles, keys, prefix) {
  slot.node.dataset.anyluminoKey = keys[index] ?? "";
  slot.title.label = titleFor(index, titles, prefix);
  slot.title.caption = slot.title.label;
}

export function measuredContentHeight(node, options = {}) {
  if (!node) {
    return 0;
  }

  const includeSelf = options.includeSelf ?? true;
  const nodeRect = node.getBoundingClientRect();
  let height = includeSelf ? Math.max(node.scrollHeight, node.offsetHeight, nodeRect.height) : 0;
  const measureChildren = (parent) => {
    for (const child of parent.children) {
      const childRect = child.getBoundingClientRect();
      // A display:contents wrapper, such as an anywidget mount root, has no
      // box of its own; measure through it so its content still counts. Its
      // all-zero rect would otherwise measure as -nodeRect.top, which is
      // positive while the node is scrolled above the viewport.
      if (childRect.width === 0 && childRect.height === 0 && child.children.length > 0) {
        measureChildren(child);
        continue;
      }
      const childHeight = Math.max(child.scrollHeight, child.offsetHeight, childRect.bottom - nodeRect.top);
      if (childHeight <= 0 && child.children.length > 0) {
        measureChildren(child);
        continue;
      }
      height = Math.max(height, childHeight);
    }
  };
  measureChildren(node);
  return Math.ceil(height);
}

/**
 * Collapse a burst of trait changes into one pass. A single Python mutation
 * arrives as several change events, and rebuilding once per event remounts
 * every child repeatedly.
 */
export function coalesce(callback) {
  let scheduled = false;
  return () => {
    if (scheduled) {
      return;
    }
    scheduled = true;
    queueMicrotask(() => {
      scheduled = false;
      callback();
    });
  };
}

/**
 * Index existing child slots by the widget ref they render, so rebuilding a
 * panel can reuse them instead of remounting every child. `take` hands back one
 * slot per matching ref and `rest` reports the slots that are no longer
 * composed.
 */
export function reusableSlots(slots) {
  const byRef = new Map();
  for (const slot of slots) {
    const ref = slot.node.dataset.anyluminoRef;
    byRef.set(ref, [...(byRef.get(ref) ?? []), slot]);
  }
  return {
    take: (ref) => byRef.get(ref)?.shift(),
    rest: () => [...byRef.values()].flat(),
  };
}

/**
 * Bind and unbind a set of model listeners as one unit.
 */
export function modelListeners(model, bindings) {
  for (const [name, callback] of bindings) {
    model.on(`change:${name}`, callback);
  }
  return () => {
    for (const [name, callback] of bindings) {
      removeModelListener(model, `change:${name}`, callback);
    }
  };
}

const CHILD_ERROR_STYLE = [
  "padding: 8px 10px",
  "color: #b42318",
  "background: #fef3f2",
  "border: 1px solid #fda29b",
  "border-radius: 4px",
  "font-size: 12px",
  "white-space: pre-wrap",
].join("; ");

/**
 * Replace a child slot with an inline failure notice. Styled here rather than
 * in a stylesheet because every layout family ships its own CSS asset.
 */
export function renderChildError(node, error) {
  const message = document.createElement("div");
  message.className = "anylumino-ChildError";
  message.setAttribute("style", CHILD_ERROR_STYLE);
  message.textContent = `[anylumino] Child failed to render: ${String(error?.message ?? error)}`;
  node.replaceChildren(message);
}

export function removeModelListener(model, eventName, callback) {
  try {
    model.off(eventName, callback);
  } catch {
    model.off(eventName, callback, null);
  }
}

export function combineSignals(parentSignal, localSignal) {
  if (AbortSignal.any) {
    return AbortSignal.any([parentSignal, localSignal]);
  }
  if (parentSignal.aborted || localSignal.aborted) {
    const controller = new AbortController();
    controller.abort();
    return controller.signal;
  }
  const controller = new AbortController();
  const abort = () => controller.abort();
  parentSignal.addEventListener("abort", abort, { once: true });
  localSignal.addEventListener("abort", abort, { once: true });
  return controller.signal;
}

// anywidget renders as soon as a widget module is ready, which can happen before the notebook
// attaches the output node, and Lumino refuses to attach a widget to a detached host.
// Remove once an anywidget release includes manzt/anywidget#1029.
export function whenConnected(node, signal) {
  if (node.isConnected) {
    return Promise.resolve(true);
  }
  if (signal?.aborted) {
    return Promise.resolve(false);
  }
  return new Promise((resolve) => {
    let frame = 0;
    const stop = () => {
      cancelAnimationFrame(frame);
      resolve(false);
    };
    const check = () => {
      if (node.isConnected) {
        signal?.removeEventListener("abort", stop);
        resolve(true);
        return;
      }
      frame = requestAnimationFrame(check);
    };
    signal?.addEventListener("abort", stop, { once: true });
    frame = requestAnimationFrame(check);
  });
}

export function dispatchResize(target) {
  try {
    target.dispatchEvent(new Event("resize"));
  } catch {
    // Embedded documents can reject synthetic events during teardown.
  }
}

export function resizeEmbeddedDocument(contentWindow) {
  dispatchResize(contentWindow);
  const handlers = contentWindow?.Lib?.Handler?.handlers;
  if (!handlers?.values) {
    return;
  }
  for (const handler of handlers.values()) {
    if (typeof handler?.reSize === "function") {
      handler.reSize();
    }
  }
}

const SUPPRESS_SHORTCUTS = "data-lm-suppress-shortcuts";

// Lumino's command registry skips key bindings for events from inside this attribute,
// but it tests a binding's selector on each node before the attribute on the next one.
// JupyterLab's command-mode selectors match the focused node itself, so the attribute
// also goes on whichever node inside the root holds focus.
export function installShortcutSuppression(model, root, signal) {
  const tagged = new WeakSet();
  const sync = () => root.toggleAttribute(SUPPRESS_SHORTCUTS, Boolean(model.get("suppress_shortcuts")));
  root.addEventListener(
    "focusin",
    (event) => {
      const target = event.target;
      if (model.get("suppress_shortcuts") && target !== root && !target.hasAttribute(SUPPRESS_SHORTCUTS)) {
        target.setAttribute(SUPPRESS_SHORTCUTS, "");
        tagged.add(target);
      }
    },
    { signal },
  );
  root.addEventListener(
    "focusout",
    (event) => {
      if (tagged.delete(event.target)) {
        event.target.removeAttribute(SUPPRESS_SHORTCUTS);
      }
    },
    { signal },
  );
  sync();
  return sync;
}

// Lumino only refits on its own resize messages, so a host that changes the
// panel's width without a window resize, such as a collapsing sidebar, needs this.
export function observeResize(element, callback, signal) {
  const observer = new ResizeObserver(() => callback());
  observer.observe(element);
  signal.addEventListener("abort", () => observer.disconnect(), { once: true });
}

/**
 * Return the visible slots a click may have revealed, and record which slots are shown in
 * `shown`, a WeakSet the caller keeps between calls.
 *
 * A slot counts as revealed when it was not shown at the last call or has not rendered yet,
 * such as an accordion section the click opened. Slots that were already shown are left out:
 * a visibility notice resizes embedded documents, which resets a chart's visible range.
 */
export function revealedSlots(slots, shown, isVisible) {
  const revealed = [];
  for (const slot of slots) {
    if (!isVisible(slot)) {
      shown.delete(slot);
    } else if (!shown.has(slot) || slot.node.dataset.anyluminoRendered === "false") {
      shown.add(slot);
      revealed.push(slot);
    }
  }
  return revealed;
}

/**
 * Return a function that watches the content of the given nodes and calls
 * `callback` when it changes size, until `signal` aborts; each call replaces
 * the watched nodes.
 *
 * A child can resize its content after it renders, such as a chart whose frame
 * grows with its panes, so the watch covers content boxes a few levels deep: an
 * outer box that fills its slot does not change with its content. display:contents
 * mount roots have no box and are walked through. Added and removed nodes, such
 * as a closing popup, count too, since they change the height without resizing a
 * watched box.
 */
export function contentObserver(callback, signal, depth = 4) {
  const resizes = new ResizeObserver(() => callback());
  const mutations = new MutationObserver(() => callback());
  signal.addEventListener(
    "abort",
    () => {
      resizes.disconnect();
      mutations.disconnect();
    },
    { once: true },
  );
  const visit = (parent, remaining) => {
    for (const child of parent.children) {
      const contents = getComputedStyle(child).display === "contents";
      if (!contents) {
        resizes.observe(child);
      }
      if (contents || remaining > 1) {
        visit(child, contents ? remaining : remaining - 1);
      }
    }
  };
  return (nodes) => {
    resizes.disconnect();
    mutations.disconnect();
    for (const node of nodes) {
      visit(node, depth);
      mutations.observe(node, { childList: true, subtree: true });
    }
  };
}

export function disposeLuminoWidget(widget) {
  if (!widget || widget.isDisposed) {
    return;
  }
  try {
    widget.dispose();
  } catch (error) {
    if (!String(error?.message ?? error).includes("Widget is not attached")) {
      throw error;
    }
  }
}

export async function renderWidgetRef(model, host, ref, el, signal) {
  try {
    const child = await host.getWidget(ref);
    await child.render({ el, signal });
    return;
  } catch (error) {
    if (!isMissingAnywidgetBinding(error)) {
      throw error;
    }
  }

  const manager = model.widget_manager;
  if (!manager?.get_model || !manager?.create_view) {
    throw new Error("[anylumino] The current widget manager cannot render ipywidgets controls.");
  }

  const childModel = await manager.get_model(modelIdFromRef(ref));
  const childView = await manager.create_view(childModel);
  if (signal.aborted) {
    childView.remove?.();
    return;
  }

  el.replaceChildren(childView.el);
  signal.addEventListener("abort", () => childView.remove?.(), { once: true });
}

export function installResizeHandle(model, root, onResize, signal, options = {}) {
  const handle = document.createElement("div");
  handle.className = "anylumino-ResizeHandle";
  handle.title = "Resize";
  root.appendChild(handle);

  const minWidth = Number(options.minWidth ?? 260);
  const minHeight = Number(options.minHeight ?? 160);

  const syncHandle = () => {
    const enabled = Boolean(model.get("resizable"));
    handle.hidden = !enabled;
    root.classList.toggle("anylumino-mod-resizable", enabled);
  };

  const onPointerDown = (event) => {
    if (!model.get("resizable")) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    try {
      handle.setPointerCapture(event.pointerId);
    } catch {
      // Synthetic pointer events used by browser tests do not always create capture state.
    }

    const startX = event.clientX;
    const startY = event.clientY;
    const startRect = root.getBoundingClientRect();

    const onPointerMove = (moveEvent) => {
      const nextWidth = Math.max(minWidth, Math.round(startRect.width + moveEvent.clientX - startX));
      const nextHeight = Math.max(minHeight, Math.round(startRect.height + moveEvent.clientY - startY));
      root.style.width = `${nextWidth}px`;
      root.style.height = `${nextHeight}px`;
      onResize();
    };

    const onPointerUp = () => {
      try {
        handle.releasePointerCapture(event.pointerId);
      } catch {
        // Ignore missing capture state during synthetic browser tests.
      }
      handle.removeEventListener("pointermove", onPointerMove);
      handle.removeEventListener("pointerup", onPointerUp);
      handle.removeEventListener("pointercancel", onPointerUp);

      const rect = root.getBoundingClientRect();
      model.set("width", `${Math.round(rect.width)}px`);
      model.set("height", `${Math.round(rect.height)}px`);
      model.save_changes();
      onResize();
    };

    handle.addEventListener("pointermove", onPointerMove);
    handle.addEventListener("pointerup", onPointerUp);
    handle.addEventListener("pointercancel", onPointerUp);
  };

  syncHandle();
  handle.addEventListener("pointerdown", onPointerDown, { signal });
  model.on("change:resizable", syncHandle);
  signal.addEventListener(
    "abort",
    () => {
      removeModelListener(model, "change:resizable", syncHandle);
    },
    { once: true },
  );

  return handle;
}

export function notifyLuminoWidgetVisible(widget, options = {}) {
  widget.update();
  notifyNodeVisible(widget.node, options);
}

/**
 * Tell size-sensitive content under `node`, such as Plotly plots and embedded
 * documents, that it is visible again after being hidden or resized.
 */
export function notifyNodeVisible(node, options = {}) {
  const notify = () => {
    if (options.dispatchWindowResize) {
      dispatchResize(window);
    }
    const plotly = window.Plotly;
    for (const plot of node.querySelectorAll(".js-plotly-plot")) {
      try {
        if (typeof plotly?.Plots?.resize === "function") {
          plotly.Plots.resize(plot);
        } else {
          dispatchResize(plot);
        }
      } catch {
        dispatchResize(plot);
      }
    }
    for (const iframe of node.querySelectorAll("iframe")) {
      if (iframe.contentWindow) {
        resizeEmbeddedDocument(iframe.contentWindow);
      }
    }
  };
  requestAnimationFrame(() => {
    notify();
    requestAnimationFrame(notify);
  });
}
