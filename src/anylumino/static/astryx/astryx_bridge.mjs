const UNSAFE_REACT_PROPS = ["children", "dangerouslySetInnerHTML", "ref", "key"];


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


export function registeredComponent(components, name) {
  const component = components[name];
  if (component === undefined) {
    const registered = Object.keys(components).sort().join(", ");
    throw new Error(`[anylumino] Unknown Astryx component "${name}". Registered components: ${registered}`);
  }
  return component;
}
