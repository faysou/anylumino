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
  for (const child of node.children) {
    const childRect = child.getBoundingClientRect();
    height = Math.max(height, child.scrollHeight, child.offsetHeight, childRect.bottom - nodeRect.top);
  }
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
  const notify = () => {
    if (options.dispatchWindowResize) {
      dispatchResize(window);
    }
    const plotly = window.Plotly;
    for (const plot of widget.node.querySelectorAll(".js-plotly-plot")) {
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
    for (const iframe of widget.node.querySelectorAll("iframe")) {
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
