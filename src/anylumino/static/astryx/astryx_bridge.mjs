const UNSAFE_REACT_PROPS = ["children", "dangerouslySetInnerHTML", "ref", "key"];

const JUPYTERLAB_LIGHT_ATTRIBUTE = "data-jp-theme-light";


export function modelProps(model, reserved = []) {
  const props = { ...(model.get("props") ?? {}) };
  for (const name of [...UNSAFE_REACT_PROPS, ...reserved]) {
    delete props[name];
  }
  return props;
}


export function setModelOpen(model, isOpen) {
  const nextOpen = Boolean(isOpen);
  model.set("is_open", nextOpen);
  model.save_changes();
  model.send({ type: "open", is_open: nextOpen });
}


export function sendModelAction(model, value, action) {
  const message = { type: "click" };
  if (value !== undefined) {
    message.value = value;
  }
  if (action !== undefined) {
    message.action = action;
  }
  model.send(message);
}


export function toggleGroupValue(value, isMultiple) {
  if (isMultiple) {
    return Array.isArray(value) ? value.map(String) : [];
  }
  return value == null || value === "" ? null : String(value);
}


export function registeredComponent(components, name) {
  const component = components[name];
  if (component === undefined) {
    const registered = Object.keys(components).sort().join(", ");
    throw new Error(`[anylumino] Unknown Astryx component "${name}". Registered components: ${registered}`);
  }
  return component;
}


/**
 * Identity of the child widgets a model currently composes, including the
 * component that lays them out. Re-rendering the React tree keeps mounted
 * children in place, so children are only torn down and rendered again when
 * this signature changes.
 */
export function childSignature(model) {
  const refs = model.get("widgets") ?? [];
  const keys = model.get("child_keys") ?? [];
  const name = String(model.get("component_name") || model.get("component_kind") || "");
  return [name, ...refs.map((ref, index) => `${keys[index] ?? ""} ${ref}`)].join(" ");
}


/**
 * Resolve the Astryx `Theme` mode for a color mode that Astryx does not know.
 * JupyterLab marks its own light and dark themes on the document body.
 */
export function resolveColorMode(mode, documentRef = globalThis.document) {
  if (mode !== "jupyterlab") {
    return mode;
  }
  const light = documentRef?.body?.getAttribute?.(JUPYTERLAB_LIGHT_ATTRIBUTE);
  if (light === null || light === undefined) {
    return "system";
  }
  return light === "false" ? "dark" : "light";
}


/**
 * Watch the JupyterLab theme attribute and report the resolved mode. Every
 * widget shares one observer because the attribute is document-wide.
 */
export function observeJupyterLabTheme(onChange, documentRef = globalThis.document) {
  const body = documentRef?.body;
  if (!body || typeof MutationObserver === "undefined") {
    return () => {};
  }
  const observer = new MutationObserver(() => onChange(resolveColorMode("jupyterlab", documentRef)));
  observer.observe(body, { attributeFilter: [JUPYTERLAB_LIGHT_ATTRIBUTE] });
  return () => observer.disconnect();
}


/**
 * Astryx `Slider` works in linear steps, so a logarithmic control drives it in
 * exponent space and reports `base ** exponent` as its value.
 */
export function logExponent(value, base, minExponent, maxExponent) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric) || numeric <= 0) {
    return minExponent;
  }
  const exponent = Math.log(numeric) / Math.log(base);
  return Math.min(maxExponent, Math.max(minExponent, exponent));
}

export function logValue(exponent, base) {
  return base ** Number(exponent);
}


/**
 * Relative pane sizes of a split panel as fractions that sum to one. Panes
 * without a size share what the sized panes leave, or the whole panel when
 * none is sized.
 */
export function paneFractions(sizes, count) {
  if (count <= 0) {
    return [];
  }
  const given = (Array.isArray(sizes) ? sizes : []).slice(0, count).map((size) => Math.max(0, Number(size) || 0));
  const missing = count - given.length;
  const total = given.reduce((sum, size) => sum + size, 0);
  if (total <= 0) {
    return Array.from({ length: count }, () => 1 / count);
  }
  const share = missing > 0 ? total / given.length : 0;
  const fractions = [...given, ...Array.from({ length: missing }, () => share)];
  const sum = fractions.reduce((acc, fraction) => acc + fraction, 0);
  return fractions.map((fraction) => fraction / sum);
}

/**
 * Fractions after the pane at `index` is dragged to `fraction`. Only the last
 * pane absorbs the change, so the other panes keep their sizes.
 */
export function fractionsWithPane(fractions, index, fraction) {
  const next = [...fractions];
  const last = next.length - 1;
  if (index < 0 || index >= last) {
    return next;
  }
  const others = next.reduce((sum, value, position) => (position === index || position === last ? sum : sum + value), 0);
  next[index] = Math.min(Math.max(Number(fraction) || 0, 0), Math.max(0, 1 - others));
  next[last] = Math.max(0, 1 - others - next[index]);
  return next.map((value) => Math.round(value * 1e4) / 1e4);
}
