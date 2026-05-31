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
