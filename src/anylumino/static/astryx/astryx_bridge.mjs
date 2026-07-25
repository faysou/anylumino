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
