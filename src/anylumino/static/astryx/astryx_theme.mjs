/**
 * Document-level theme handling for Astryx widgets.
 *
 * Each anywidget renders in its own React root, so every widget mounts a root
 * Astryx `Theme`, and each one syncs `html[data-theme]` to the document. In a
 * notebook that means the last widget to mount decides the page attribute and
 * the first widget to unmount clears it, leaving the page with no mode even
 * though other outputs are still on screen.
 *
 * anylumino restores the value the host page started with once the last Astryx
 * widget goes away. It deliberately does not police the attribute while widgets
 * are alive: writing to `html` invalidates style for the whole document, so
 * correcting every write turns into a style-recalc war with Astryx's own layout
 * effect that can stall a notebook for seconds at a time.
 */

let guardCount = 0;
let hostTheme = null;

/**
 * Remember the host page's color mode for as long as Astryx widgets are
 * mounted. Returns a release function; the value is restored once every widget
 * has released it.
 */
export function claimDocumentTheme(documentRef = globalThis.document) {
  const root = documentRef?.documentElement;
  if (!root) {
    return () => {};
  }

  if (guardCount === 0) {
    hostTheme = root.getAttribute("data-theme");
  }
  guardCount += 1;

  let released = false;
  return () => {
    if (released) {
      return;
    }
    released = true;
    guardCount -= 1;
    if (guardCount > 0) {
      return;
    }
    if (hostTheme === null) {
      root.removeAttribute("data-theme");
    } else {
      root.setAttribute("data-theme", hostTheme);
    }
    hostTheme = null;
  };
}

export function hashString(value) {
  let hash = 5381;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 33) ^ value.charCodeAt(index);
  }
  return (hash >>> 0).toString(36);
}

/**
 * Inject theme CSS once per distinct stylesheet and keep a reference count, so
 * a widget unmounting never strips tokens from the widgets that remain. Astryx
 * dedupes by theme name and drops the shared tag with the first unmount.
 *
 * `styleRoot` is the document or the shadow root that contains the widget. A
 * style tag in `document.head` does not reach into a shadow root, which is
 * where hosts such as marimo mount every anywidget.
 */
export function claimThemeCSS(themeName, css, styleRoot = globalThis.document) {
  const text = typeof css === "string" ? css.trim() : "";
  if (!text || !styleRoot) {
    return () => {};
  }

  const styleKey = `${themeName}-${hashString(text)}`;
  const selector = `style[data-anylumino-astryx-theme-id="${styleKey}"]`;
  const matches = [...styleRoot.querySelectorAll(selector)];
  let element = matches[0];
  for (const duplicate of matches.slice(1)) {
    duplicate.remove();
  }

  if (element) {
    element.setAttribute("data-anylumino-astryx-theme-count", String(themeCSSCount(element) + 1));
  } else {
    element = (styleRoot.ownerDocument ?? styleRoot).createElement("style");
    element.setAttribute("data-anylumino-astryx-theme", themeName);
    element.setAttribute("data-anylumino-astryx-theme-id", styleKey);
    element.setAttribute("data-anylumino-astryx-theme-count", "1");
    element.textContent = text;
    (styleRoot.head ?? styleRoot).appendChild(element);
  }

  let released = false;
  return () => {
    if (released || !element.isConnected) {
      return;
    }
    released = true;
    const count = themeCSSCount(element) - 1;
    if (count <= 0) {
      element.remove();
    } else {
      element.setAttribute("data-anylumino-astryx-theme-count", String(count));
    }
  };
}

function themeCSSCount(element) {
  return Number(element.getAttribute("data-anylumino-astryx-theme-count") || "0");
}
