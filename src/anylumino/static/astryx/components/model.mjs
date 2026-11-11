

export function componentName(model) {
  return String(model.get("component_name") || model.get("component_kind") || "Stack");
}

export function textFor(model) {
  return String(model.get("text") || model.get("label") || model.get("value") || "");
}

export function setModelValue(model, value) {
  model.set("value", value);
  model.save_changes();
}

export function continuousUpdate(model) {
  return model.get("continuous_update") !== false;
}

export function setBooleanValue(model, value) {
  setModelValue(model, Boolean(value));
}

export function setStringValue(model, value) {
  setModelValue(model, value == null ? "" : String(value));
}

export function setNullableStringValue(model, value) {
  setModelValue(model, value == null ? null : String(value));
}

export function setNumberValue(model, value) {
  setModelValue(model, value == null || value === "" ? null : Number(value));
}

export function setArrayValue(model, value) {
  setModelValue(model, Array.isArray(value) ? value : []);
}

export function setItemValue(model, item) {
  setModelValue(model, item == null ? null : String(item.id ?? item.value ?? item.label ?? ""));
}

export function setItemArrayValue(model, items) {
  setArrayValue(model, asArray(items).map((item) => String(item.id ?? item.value ?? item.label ?? "")));
}

export function fileInputValue(files, isMultiple) {
  if (!files) {
    return isMultiple ? [] : null;
  }
  const fileList = Array.isArray(files) ? files : [files];
  const records = fileList.map((file) => ({
    name: file.name,
    size: file.size,
    type: file.type,
    lastModified: file.lastModified,
  }));
  return isMultiple ? records : (records[0] ?? null);
}

export function asArray(value) {
  return Array.isArray(value) ? value : [];
}

export function rawProps(model) {
  return { ...(model.get("props") ?? {}) };
}

/**
 * Select the current content when a field gains focus, so clicking into a
 * value and typing replaces it instead of merging with the old text. The
 * timeout lets the browser finish placing the caret before the selection.
 */
export function selectAllOnFocus(event) {
  const input = event?.target;
  if (input && typeof input.select === "function") {
    setTimeout(() => input.select(), 0);
  }
}

/**
 * Wire a deferred-update control: the draft drives the visible value and the
 * model only learns about it when the edit ends.
 */
export function draftHandlers(model, draft, { commitOnEnter = false } = {}) {
  return {
    onChange: (nextValue) => draft.set(nextValue),
    onBlur: () => draft.commit(model),
    ...(commitOnEnter ? { onEnter: () => draft.commit(model) } : {}),
  };
}

/**
 * The shared traits a spec lists in `traits`, as the same-named Astryx props:
 * `disabled` becomes `isDisabled`. Empty and false values are left out, so a
 * component only receives what its wrapper set.
 */
export function traitProps(model, traits = []) {
  const values = {
    label: ["label", model.get("label")],
    variant: ["variant", model.get("variant")],
    disabled: ["isDisabled", model.get("disabled")],
    icon: ["icon", model.get("icon")],
  };
  const forwarded = {};
  for (const trait of traits) {
    const [prop, value] = values[trait];
    if (value) {
      forwarded[prop] = value;
    }
  }
  return forwarded;
}
