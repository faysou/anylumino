import "@spectrum-web-components/theme/sp-theme.js";
import "@spectrum-web-components/theme/theme-light.js";
import "@spectrum-web-components/theme/theme-dark.js";
import "@spectrum-web-components/theme/scale-medium.js";
import "@spectrum-web-components/icon/sp-icon.js";
import "@spectrum-web-components/badge/sp-badge.js";
import "@spectrum-web-components/button/sp-button.js";
import "@spectrum-web-components/action-button/sp-action-button.js";
import "@spectrum-web-components/checkbox/sp-checkbox.js";
import "@spectrum-web-components/color-field/sp-color-field.js";
import "@spectrum-web-components/combobox/sp-combobox.js";
import "@spectrum-web-components/divider/sp-divider.js";
import "@spectrum-web-components/field-label/sp-field-label.js";
import "@spectrum-web-components/link/sp-link.js";
import "@spectrum-web-components/menu/sp-menu-item.js";
import "@spectrum-web-components/meter/sp-meter.js";
import "@spectrum-web-components/number-field/sp-number-field.js";
import "@spectrum-web-components/picker/sync/sp-picker.js";
import "@spectrum-web-components/progress-bar/sp-progress-bar.js";
import "@spectrum-web-components/radio/sp-radio.js";
import "@spectrum-web-components/radio/sp-radio-group.js";
import "@spectrum-web-components/search/sp-search.js";
import "@spectrum-web-components/slider/sync/sp-slider.js";
import "@spectrum-web-components/slider/sp-slider-handle.js";
import "@spectrum-web-components/status-light/sp-status-light.js";
import "@spectrum-web-components/switch/sp-switch.js";
import "@spectrum-web-components/tags/sp-tag.js";
import "@spectrum-web-components/tags/sp-tags.js";
import "@spectrum-web-components/textfield/sp-textfield.js";
import "./spectrum_icons.js";

function optionParts(option) {
  if (Array.isArray(option) && option.length === 2) {
    return { label: String(option[0]), value: option[1] };
  }
  return { label: String(option), value: option };
}

function optionKey(value) {
  return JSON.stringify(value);
}

function spectrumTheme(child, model = null) {
  const theme = document.createElement("sp-theme");
  theme.className = "anylumino-SpectrumTheme";
  theme.color = String(model?.get("spectrum_color") ?? "light");
  theme.scale = String(model?.get("spectrum_scale") ?? "medium");
  theme.append(child);
  return theme;
}

function updateModel(model, value) {
  model.set("value", value);
  model.save_changes();
}

function labelText(model) {
  return String(model.get("description") ?? "");
}

function controlShell(model, control) {
  const shell = document.createElement("div");
  shell.className = "anylumino-Control";
  shell.dataset.kind = String(model.get("control_kind") ?? "text");

  const description = labelText(model);
  if (description && !control.hasAttribute("label")) {
    const label = document.createElement("sp-field-label");
    label.textContent = description;
    label.for = control.id || `${model.model_id}-control`;
    control.id = control.id || label.for;
    shell.append(label);
  }

  shell.append(control);
  return spectrumTheme(shell, model);
}

function syncDisabled(model, element) {
  element.disabled = Boolean(model.get("disabled"));
}

function setIfDefined(element, name, value) {
  if (value === undefined || value === null || value === "") {
    element.removeAttribute(name);
    return;
  }
  element.setAttribute(name, String(value));
}

function setBoolAttribute(element, name, value) {
  if (Boolean(value)) {
    element.setAttribute(name, "");
  } else {
    element.removeAttribute(name);
  }
}

function spectrumButtonVariant(style) {
  const value = String(style ?? "").trim();
  if (value === "danger" || value === "negative") return "negative";
  if (value === "primary" || value === "success" || value === "brand") return "accent";
  if (value === "secondary") return "secondary";
  return "primary";
}

function workflowIconName(rawName) {
  const name = String(rawName ?? "").trim();
  const aliases = {
    "chart-line": "GraphTrend",
    "circle-half-stroke": "Light",
    "circle-info": "InfoCircle",
    "circle-question": "HelpCircle",
    "comment": "Comment",
    "expand": "FullScreen",
    "forward-step": "StepForward",
    "plus": "AddContent",
    "rotate-left": "RotateRight",
    "rotate": "RotateRight",
    "upload": "Upload",
    "clock": "ClockPending",
  };
  if (aliases[name]) return aliases[name];
  return name
    .split(/[-_\s]+/u)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join("");
}

function kebabName(name) {
  return String(name)
    .replace(/([a-z0-9])([A-Z])/g, "$1-$2")
    .replace(/_/g, "-")
    .toLowerCase();
}

function iconSpec(model, source) {
  const raw = typeof source === "object" && source !== null ? source : { name: source };
  const name = String(raw.name ?? raw.icon ?? "").trim();
  const src = String(raw.src ?? raw.icon_src ?? model.get("icon_src") ?? "").trim();
  if (!name && !src) {
    return null;
  }
  return {
    name: workflowIconName(name),
    src,
    size: String(raw.size ?? raw.icon_size ?? model.get("icon_size") ?? "s"),
    label: String(raw.label ?? raw.icon_label ?? ""),
  };
}

function createIcon(model, source) {
  const spec = iconSpec(model, source);
  if (!spec) {
    return null;
  }
  if (spec.src) {
    const icon = document.createElement("sp-icon");
    icon.className = "anylumino-SpectrumIcon";
    icon.src = spec.src;
    icon.size = spec.size;
    icon.slot = "icon";
    if (spec.label) {
      icon.label = spec.label;
    } else {
      icon.setAttribute("aria-hidden", "true");
    }
    return icon;
  }

  const tagName = `sp-icon-${kebabName(spec.name)}`;
  const icon = document.createElement(tagName);
  icon.className = "anylumino-SpectrumIcon";
  icon.size = spec.size;
  icon.slot = "icon";
  if (spec.label) {
    icon.label = spec.label;
  } else {
    icon.setAttribute("aria-hidden", "true");
  }
  return icon;
}

function datetimeLocalValue(value) {
  const text = String(value ?? "");
  if (!text) return "";
  return text.replace(" ", "T").replace(/([+-]\d{2}:?\d{2}|Z)$/u, "");
}

function datetimeParts(value) {
  const [date = "", time = ""] = datetimeLocalValue(value).split("T");
  return { date, time: time.slice(0, 5) };
}

function joinDatetimeParts(date, time) {
  if (!date && !time) return "";
  return `${date || "1970-01-01"}T${time || "00:00"}`;
}

function normalizeTime(value) {
  return String(value ?? "").slice(0, 5);
}

function inputValue(value, type) {
  if (type === "datetime-local") return datetimeLocalValue(value);
  return String(value ?? "");
}

function makeTextfield(model, type = "text", tagName = "sp-textfield") {
  const input = document.createElement(tagName);
  input.className = "anylumino-SpectrumField";
  input.value = inputValue(model.get("value"), type);
  input.placeholder = String(model.get("placeholder") ?? "");
  input.label = labelText(model);
  input.type = type;
  input.size = String(model.get("spectrum_size") ?? "m");
  setBoolAttribute(input, "quiet", model.get("quiet"));
  syncDisabled(model, input);
  setIfDefined(input, "min", inputValue(model.get("min"), type));
  setIfDefined(input, "max", inputValue(model.get("max"), type));
  setIfDefined(input, "step", model.get("step"));

  const eventName = model.get("continuous_update") ? "input" : "change";
  input.addEventListener(eventName, () => {
    const numeric = ["number", "range"].includes(type);
    updateModel(model, numeric ? Number(input.value) : input.value);
  });
  return controlShell(model, input);
}

function createTimePicker(model, value, onValueChanged) {
  const wrap = document.createElement("div");
  wrap.className = "anylumino-TimePicker";

  const input = document.createElement("input");
  input.className = "anylumino-NativeInput anylumino-TimeInput";
  input.type = "time";
  input.value = normalizeTime(value);
  syncDisabled(model, input);

  const button = document.createElement("sp-action-button");
  button.className = "anylumino-TimePickerButton";
  button.title = "Open time picker";
  button.label = "Open time picker";
  button.disabled = Boolean(model.get("disabled"));
  const icon = createIcon(model, "clock");
  if (icon) button.append(icon);

  const popup = document.createElement("div");
  popup.className = "anylumino-TimePickerPopup";
  popup.hidden = true;

  const columns = document.createElement("div");
  columns.className = "anylumino-TimePickerColumns";
  const hourColumn = document.createElement("div");
  hourColumn.className = "anylumino-TimePickerColumn";
  hourColumn.setAttribute("aria-label", "Hours");
  const minuteColumn = document.createElement("div");
  minuteColumn.className = "anylumino-TimePickerColumn";
  minuteColumn.setAttribute("aria-label", "Minutes");

  const timeParts = () => {
    const [hour = "00", minute = "00"] = normalizeTime(input.value).split(":");
    return { hour: hour.padStart(2, "0"), minute: minute.padStart(2, "0") };
  };
  const joinTimeParts = (hour, minute) => `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;

  const createOption = (value, part) => {
    const item = document.createElement("sp-action-button");
    item.className = "anylumino-TimePickerOption";
    item.textContent = value;
    item.dataset.value = value;
    item.dataset.part = part;
    item.addEventListener("click", () => {
      const current = timeParts();
      input.value = part === "hour" ? joinTimeParts(value, current.minute) : joinTimeParts(current.hour, value);
      onValueChanged(input.value);
      syncSelection();
      if (part === "minute") hidePicker();
      input.focus();
    });
    return item;
  };

  for (let hour = 0; hour < 24; hour += 1) hourColumn.append(createOption(String(hour).padStart(2, "0"), "hour"));
  for (let minute = 0; minute < 60; minute += 1) minuteColumn.append(createOption(String(minute).padStart(2, "0"), "minute"));
  columns.append(hourColumn, minuteColumn);
  popup.append(spectrumTheme(columns, model));

  const syncSelection = () => {
    const current = timeParts();
    popup.querySelectorAll(".anylumino-TimePickerOption").forEach((item) => {
      item.selected =
        (item.dataset.part === "hour" && item.dataset.value === current.hour) ||
        (item.dataset.part === "minute" && item.dataset.value === current.minute);
    });
  };
  wrap._anyluminoSyncTimeSelection = syncSelection;

  const positionPopup = () => {
    if (popup.hidden) return;
    const rect = wrap.getBoundingClientRect();
    popup.style.left = `${Math.max(8, Math.min(rect.left, window.innerWidth - 232))}px`;
    popup.style.top = `${Math.min(rect.bottom + 4, window.innerHeight - 252)}px`;
    popup.style.width = `${Math.max(180, Math.min(rect.width, 224))}px`;
  };
  const hidePicker = () => {
    popup.hidden = true;
    window.removeEventListener("resize", positionPopup);
    document.removeEventListener("scroll", positionPopup, true);
  };
  const showPicker = () => {
    if (Boolean(model.get("disabled"))) return;
    syncSelection();
    popup.hidden = false;
    positionPopup();
    window.addEventListener("resize", positionPopup);
    document.addEventListener("scroll", positionPopup, true);
  };
  const togglePicker = () => (popup.hidden ? showPicker() : hidePicker());

  const eventName = model.get("continuous_update") ? "input" : "change";
  input.addEventListener(eventName, () => {
    onValueChanged(input.value);
    syncSelection();
  });
  input.addEventListener("click", showPicker);
  button.addEventListener("click", (event) => {
    event.preventDefault();
    togglePicker();
  });
  wrap.addEventListener("focusout", (event) => {
    if (event.relatedTarget instanceof Node && (wrap.contains(event.relatedTarget) || popup.contains(event.relatedTarget))) return;
    hidePicker();
  });
  popup.addEventListener("focusout", (event) => {
    if (event.relatedTarget instanceof Node && (wrap.contains(event.relatedTarget) || popup.contains(event.relatedTarget))) return;
    hidePicker();
  });

  wrap.append(input, button);
  document.body.append(popup);
  queueMicrotask(() => {
    const observer = new MutationObserver(() => {
      if (!document.body.contains(wrap)) {
        popup.remove();
        observer.disconnect();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  });
  return wrap;
}

function makeTimeInput(model) {
  return controlShell(model, createTimePicker(model, model.get("value"), (value) => updateModel(model, value)));
}

function makeDatetimeInput(model) {
  const wrap = document.createElement("div");
  wrap.className = "anylumino-DateTimeFields";
  const parts = datetimeParts(model.get("value"));

  const dateInput = document.createElement("input");
  dateInput.className = "anylumino-NativeInput";
  dateInput.type = "date";
  dateInput.value = parts.date;
  syncDisabled(model, dateInput);

  const eventName = model.get("continuous_update") ? "input" : "change";
  const updateDatetime = () => updateModel(model, joinDatetimeParts(dateInput.value, timeInput.value));
  dateInput.addEventListener(eventName, updateDatetime);
  const timePicker = createTimePicker(model, parts.time, () => updateDatetime());
  const timeInput = timePicker.querySelector("input");

  wrap.append(dateInput, timePicker);
  return controlShell(model, wrap);
}

function makeTextarea(model) {
  const textarea = document.createElement("sp-textfield");
  textarea.className = "anylumino-SpectrumField";
  textarea.multiline = true;
  textarea.value = String(model.get("value") ?? "");
  textarea.placeholder = String(model.get("placeholder") ?? "");
  textarea.label = labelText(model);
  textarea.rows = Number(model.get("rows") ?? 4);
  textarea.size = String(model.get("spectrum_size") ?? "m");
  setBoolAttribute(textarea, "quiet", model.get("quiet"));
  syncDisabled(model, textarea);
  const eventName = model.get("continuous_update") ? "input" : "change";
  textarea.addEventListener(eventName, () => updateModel(model, textarea.value));
  return controlShell(model, textarea);
}

function makeCombobox(model) {
  const input = document.createElement("sp-combobox");
  input.className = "anylumino-SpectrumField";
  input.value = String(model.get("value") ?? "");
  input.placeholder = String(model.get("placeholder") ?? "");
  input.label = labelText(model);
  input.size = String(model.get("spectrum_size") ?? "m");
  syncDisabled(model, input);

  for (const option of model.get("options") ?? []) {
    const parts = optionParts(option);
    const item = document.createElement("sp-menu-item");
    item.value = optionKey(parts.value);
    item.textContent = parts.label;
    input.append(item);
  }

  const eventName = model.get("continuous_update") ? "input" : "change";
  input.addEventListener(eventName, () => updateModel(model, input.value));
  return controlShell(model, input);
}

function makePicker(model) {
  const picker = document.createElement("sp-picker");
  picker.className = "anylumino-SpectrumPicker";
  picker.label = labelText(model);
  picker.size = String(model.get("spectrum_size") ?? "m");
  syncDisabled(model, picker);

  const value = model.get("value");
  for (const option of model.get("options") ?? []) {
    const parts = optionParts(option);
    const item = document.createElement("sp-menu-item");
    item.value = optionKey(parts.value);
    item.textContent = parts.label;
    if (optionKey(value) === item.value) item.selected = true;
    picker.append(item);
  }
  picker.value = optionKey(value);
  picker.addEventListener("change", () => {
    const options = Array.from(model.get("options") ?? []).map(optionParts);
    const match = options.find((option) => optionKey(option.value) === picker.value);
    updateModel(model, match?.value ?? picker.value);
    model.set("index", picker.selectedIndex ?? options.findIndex((option) => optionKey(option.value) === picker.value));
    model.save_changes();
  });
  return controlShell(model, picker);
}

function makeNativeSelect(model, multiple = false) {
  const select = document.createElement("select");
  select.className = "anylumino-NativeInput anylumino-NativeSelect";
  select.multiple = multiple;
  select.size = multiple || model.get("control_kind") === "select" ? Number(model.get("rows") ?? 5) : 1;
  syncDisabled(model, select);

  const value = model.get("value");
  for (const option of model.get("options") ?? []) {
    const parts = optionParts(option);
    const item = document.createElement("option");
    item.textContent = parts.label;
    item.value = optionKey(parts.value);
    item.selected = multiple
      ? Array.isArray(value) && value.some((entry) => optionKey(entry) === item.value)
      : optionKey(value) === item.value;
    select.append(item);
  }

  select.addEventListener("change", () => {
    const options = Array.from(model.get("options") ?? []).map(optionParts);
    if (multiple) {
      updateModel(
        model,
        Array.from(select.selectedOptions).map((item) => options.find((option) => optionKey(option.value) === item.value)?.value ?? item.value),
      );
      return;
    }
    const match = options.find((option) => optionKey(option.value) === select.value);
    updateModel(model, match?.value ?? select.value);
    model.set("index", select.selectedIndex);
    model.save_changes();
  });

  return controlShell(model, select);
}

function makeRadio(model) {
  const group = document.createElement("sp-radio-group");
  group.className = "anylumino-ChoiceGroup";
  group.label = labelText(model);
  group.value = optionKey(model.get("value"));
  syncDisabled(model, group);

  for (const option of model.get("options") ?? []) {
    const parts = optionParts(option);
    const radio = document.createElement("sp-radio");
    radio.value = optionKey(parts.value);
    radio.textContent = parts.label;
    group.append(radio);
  }
  group.addEventListener("change", () => {
    const options = Array.from(model.get("options") ?? []).map(optionParts);
    const match = options.find((option) => optionKey(option.value) === group.value);
    updateModel(model, match?.value ?? group.value);
  });
  return controlShell(model, group);
}

function makeToggleButtons(model) {
  const group = document.createElement("div");
  group.className = "anylumino-Segmented";
  const value = model.get("value");
  const icons = model.get("icons") ?? [];
  const tooltips = model.get("tooltips") ?? [];

  Array.from(model.get("options") ?? []).forEach((option, index) => {
    const parts = optionParts(option);
    const button = document.createElement("sp-action-button");
    button.className = "anylumino-Segment";
    button.variant = spectrumButtonVariant(model.get("variant"));
    button.disabled = Boolean(model.get("disabled"));
    button.dataset.optionValue = optionKey(parts.value);
    button.selected = optionKey(value) === optionKey(parts.value);
    button.title = String(tooltips[index] ?? "");
    button.textContent = parts.label;
    const icon = createIcon(model, icons[index]);
    if (icon) button.prepend(icon);
    button.addEventListener("click", () => {
      updateModel(model, parts.value);
      model.set("index", index);
      model.save_changes();
    });
    group.append(button);
  });
  return controlShell(model, group);
}

function makeCheckbox(model, toggle = false) {
  const input = document.createElement(toggle ? "sp-switch" : "sp-checkbox");
  input.className = toggle ? "anylumino-SpectrumSwitch" : "anylumino-SpectrumCheckbox";
  input.checked = Boolean(model.get("value"));
  input.disabled = Boolean(model.get("disabled"));
  input.textContent = labelText(model);
  input.addEventListener("change", () => updateModel(model, input.checked));
  return spectrumTheme(input, model);
}

function makeButton(model, toggle = false) {
  const button = document.createElement(toggle ? "sp-action-button" : "sp-button");
  button.className = "anylumino-SpectrumButton";
  button.variant = spectrumButtonVariant(model.get("variant"));
  button.disabled = Boolean(model.get("disabled"));
  button.title = String(model.get("tooltip") ?? "");
  button.label = labelText(model);
  if (toggle) button.selected = Boolean(model.get("value"));

  const icon = createIcon(model, model.get("icon"));
  if (icon) button.append(icon);
  const text = labelText(model);
  if (text) button.append(document.createTextNode(text));
  button.addEventListener("click", () => {
    if (toggle) updateModel(model, !Boolean(model.get("value")));
    model.send({ type: "click" });
  });
  return spectrumTheme(button, model);
}

function makeSlider(model, range = false, log = false) {
  const slider = document.createElement("sp-slider");
  slider.className = "anylumino-SpectrumSlider";
  slider.label = labelText(model);
  slider.size = String(model.get("spectrum_size") ?? "m");
  slider.min = Number(model.get("min") ?? 0);
  slider.max = Number(model.get("max") ?? 100);
  slider.step = Number(model.get("step") ?? 1);
  slider.disabled = Boolean(model.get("disabled"));
  slider.editable = Boolean(model.get("readout"));
  setBoolAttribute(slider, "quiet", model.get("quiet"));
  if (model.get("orientation") === "vertical") slider.variant = "ramp";

  const value = model.get("value");
  const values = range ? [...(Array.isArray(value) ? value : [model.get("min"), model.get("max")])] : [value];
  if (range) {
    values.forEach((item, index) => {
      const handle = document.createElement("sp-slider-handle");
      handle.slot = "handle";
      handle.name = index === 0 ? "min" : "max";
      handle.label = index === 0 ? "Minimum" : "Maximum";
      handle.value = log ? Math.log(Number(item)) / Math.log(Number(model.get("base") || 10)) : Number(item);
      slider.append(handle);
    });
  } else {
    slider.value = log ? Math.log(Number(value)) / Math.log(Number(model.get("base") || 10)) : Number(value ?? 0);
  }
  slider.addEventListener(model.get("continuous_update") ? "input" : "change", () => {
    if (!range) {
      const next = Number(slider.value);
      updateModel(model, log ? Math.pow(Number(model.get("base") || 10), next) : next);
      return;
    }
    const current = Array.from(slider.querySelectorAll("sp-slider-handle")).map((handle) => {
      const next = Number(handle.value);
      return log ? Math.pow(Number(model.get("base") || 10), next) : next;
    });
    updateModel(model, current);
  });
  return controlShell(model, slider);
}

function makeSelectionSlider(model, range = false) {
  const options = Array.from(model.get("options") ?? []).map(optionParts);
  const selected = model.get("value");
  const indexValue = model.get("index");
  const fallbackMax = Math.max(options.length - 1, 0);
  const optionIndex = (value, fallback) => {
    const index = options.findIndex((option) => optionKey(option.value) === optionKey(value));
    return index >= 0 ? index : fallback;
  };
  const selectedIndex = range
    ? Array.isArray(selected) && selected.length >= 2
      ? [optionIndex(selected[0], 0), optionIndex(selected[1], fallbackMax)]
      : Array.isArray(indexValue) && indexValue.length >= 2
        ? [Number(indexValue[0]), Number(indexValue[1])]
        : [0, fallbackMax]
    : optionIndex(selected, Number.isFinite(Number(indexValue)) ? Number(indexValue) : 0);

  const clone = {
    get(name) {
      if (name === "min") return 0;
      if (name === "max") return Math.max(options.length - 1, 0);
      if (name === "step") return 1;
      if (name === "value") return selectedIndex;
      return model.get(name);
    },
    set: (...args) => model.set(...args),
    save_changes: () => model.save_changes(),
  };

  const shell = makeSlider(clone, range, false);
  const inputs = range ? shell.querySelectorAll("sp-slider-handle") : shell.querySelectorAll("sp-slider");
  inputs.forEach((input, index) => {
    input.addEventListener("change", () => {
      if (range) {
        const indices = Array.from(shell.querySelectorAll("sp-slider-handle")).map((item) => Number(item.value));
        const current = indices.map((item) => options[item]?.value);
        updateModel(model, current);
        model.set("index", indices);
        model.save_changes();
        return;
      }
      updateModel(model, options[Number(input.value)]?.value);
      model.set("index", Number(input.value));
      model.save_changes();
    });
    input.value = String(range ? selectedIndex[index] : selectedIndex);
  });
  return shell;
}

function makeProgress(model) {
  const progress = document.createElement("sp-progress-bar");
  progress.className = "anylumino-SpectrumProgress";
  progress.label = labelText(model);
  progress.value = Number(model.get("value") ?? 0) - Number(model.get("min") ?? 0);
  progress.max = Number(model.get("max") ?? 100) - Number(model.get("min") ?? 0);
  const style = String(model.get("variant") ?? "");
  if (style === "danger") progress.sideLabel = "Error";
  return controlShell(model, progress);
}

function makeTags(model, numeric = null) {
  const wrap = document.createElement("div");
  wrap.className = "anylumino-Tags";
  const list = document.createElement("sp-tags");
  list.className = "anylumino-TagList";
  const value = Array.isArray(model.get("value")) ? model.get("value") : [];
  for (const item of value) {
    const tag = document.createElement("sp-tag");
    tag.textContent = String(item);
    list.append(tag);
  }
  const input = document.createElement("sp-textfield");
  input.className = "anylumino-TagInput";
  input.placeholder = "Add value";
  input.disabled = Boolean(model.get("disabled"));
  input.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" || !input.value.trim()) return;
    event.preventDefault();
    const raw = input.value.trim();
    const next = numeric === "int" ? Number.parseInt(raw, 10) : numeric === "float" ? Number.parseFloat(raw) : raw;
    const currentValue = Array.isArray(model.get("value")) ? model.get("value") : [];
    if (!model.get("allow_duplicates") && currentValue.some((item) => optionKey(item) === optionKey(next))) {
      input.value = "";
      return;
    }
    updateModel(model, [...currentValue, next]);
    input.value = "";
  });
  wrap.append(list, input);
  return controlShell(model, wrap);
}

function makeFile(model) {
  const wrap = document.createElement("div");
  wrap.className = "anylumino-File";
  const buttonTheme = makeButton(model);
  const button = buttonTheme.querySelector("sp-button");
  const input = document.createElement("input");
  input.type = "file";
  input.accept = String(model.get("accept") ?? "");
  input.multiple = Boolean(model.get("multiple"));
  input.hidden = true;
  input.addEventListener("change", () => {
    updateModel(
      model,
      Array.from(input.files ?? []).map((file) => ({ name: file.name, size: file.size, type: file.type })),
    );
  });
  button.addEventListener("click", () => input.click());
  wrap.append(buttonTheme, input);
  return wrap;
}

function makeMedia(model, kind) {
  const value = String(model.get("value") ?? "");
  const node = document.createElement(kind);
  node.className = "anylumino-Media";
  if (value) node.src = value;
  if (kind !== "img") {
    node.controls = Boolean(model.get("controls"));
    node.autoplay = Boolean(model.get("autoplay"));
    node.loop = Boolean(model.get("loop"));
  }
  setIfDefined(node, "width", model.get("width"));
  setIfDefined(node, "height", model.get("height"));
  return controlShell(model, node);
}

function makeDisplay(model, html = false) {
  const node = document.createElement("div");
  node.className = "anylumino-Display";
  if (html) node.innerHTML = String(model.get("value") ?? "");
  else node.textContent = String(model.get("value") ?? "");
  return controlShell(model, node);
}

function makeStatus(model) {
  const status = document.createElement("sp-status-light");
  status.className = "anylumino-SpectrumStatus";
  status.variant = String(model.get("variant") || (Boolean(model.get("value")) ? "positive" : "negative"));
  status.textContent = labelText(model) || String(model.get("placeholder") || (model.get("value") ? "Valid" : "Invalid"));
  return controlShell(model, status);
}

function makeBadge(model) {
  const badge = document.createElement("sp-badge");
  badge.className = "anylumino-SpectrumBadge";
  badge.variant = String(model.get("variant") || "neutral");
  badge.size = String(model.get("spectrum_size") ?? "m");
  const icon = createIcon(model, model.get("icon"));
  if (icon) badge.append(icon);
  badge.append(document.createTextNode(String(model.get("value") ?? labelText(model))));
  return controlShell(model, badge);
}

function makeMeter(model) {
  const meter = document.createElement("sp-meter");
  meter.className = "anylumino-SpectrumMeter";
  meter.label = labelText(model);
  meter.variant = String(model.get("variant") || "informative");
  meter.size = String(model.get("spectrum_size") ?? "m");
  meter.progress = Number(model.get("value") ?? 0);
  setBoolAttribute(meter, "side-label", model.get("readout"));
  meter.textContent = labelText(model);
  return controlShell(model, meter);
}

function makeLink(model) {
  const link = document.createElement("sp-link");
  link.className = "anylumino-SpectrumLink";
  link.href = String(model.get("href") || model.get("value") || "#");
  link.variant = String(model.get("variant") || "primary");
  link.textContent = labelText(model) || String(model.get("value") || link.href);
  setBoolAttribute(link, "quiet", model.get("quiet"));
  syncDisabled(model, link);
  return controlShell(model, link);
}

function makeDivider(model) {
  const divider = document.createElement("sp-divider");
  divider.className = "anylumino-SpectrumDivider";
  divider.size = String(model.get("spectrum_size") ?? "m");
  setBoolAttribute(divider, "vertical", model.get("orientation") === "vertical");
  return controlShell(model, divider);
}

function renderControl(model) {
  const kind = String(model.get("control_kind") ?? "text");
  if (kind === "textarea") return makeTextarea(model);
  if (kind === "password") return makeTextfield(model, "password");
  if (kind === "combobox") return makeCombobox(model);
  if (kind === "dropdown") return makePicker(model);
  if (kind === "select") return makeNativeSelect(model);
  if (kind === "select-multiple") return makeNativeSelect(model, true);
  if (kind === "radio") return makeRadio(model);
  if (kind === "toggle-buttons") return makeToggleButtons(model);
  if (kind === "button") return makeButton(model);
  if (kind === "checkbox") return makeCheckbox(model);
  if (kind === "toggle") return makeButton(model, true);
  if (kind === "switch") return makeCheckbox(model, true);
  if (kind === "valid" || kind === "status-light") return makeStatus(model);
  if (kind === "badge") return makeBadge(model);
  if (kind === "meter") return makeMeter(model);
  if (kind === "link") return makeLink(model);
  if (kind === "divider") return makeDivider(model);
  if (kind === "search") return makeTextfield(model, "search", "sp-search");
  if (kind === "int-slider" || kind === "float-slider") return makeSlider(model);
  if (kind === "int-range-slider" || kind === "float-range-slider") return makeSlider(model, true);
  if (kind === "float-log-slider") return makeSlider(model, false, true);
  if (kind === "selection-slider") return makeSelectionSlider(model);
  if (kind === "selection-range-slider") return makeSelectionSlider(model, true);
  if (kind === "int-text" || kind === "bounded-int-text" || kind === "float-text" || kind === "bounded-float-text") return makeTextfield(model, "number", "sp-number-field");
  if (kind === "int-progress" || kind === "float-progress") return makeProgress(model);
  if (kind === "play") return makeSlider(model);
  if (kind === "date") return makeTextfield(model, "date");
  if (kind === "time") return makeTimeInput(model);
  if (kind === "datetime") return makeDatetimeInput(model);
  if (kind === "color") return makeTextfield(model, "text", "sp-color-field");
  if (kind === "tags") return makeTags(model);
  if (kind === "colors") return makeTags(model);
  if (kind === "ints") return makeTags(model, "int");
  if (kind === "floats") return makeTags(model, "float");
  if (kind === "file") return makeFile(model);
  if (kind === "image") return makeMedia(model, "img");
  if (kind === "audio") return makeMedia(model, "audio");
  if (kind === "video") return makeMedia(model, "video");
  if (kind === "html" || kind === "output") return makeDisplay(model, true);
  if (kind === "label") return makeDisplay(model, false);
  return makeTextfield(model, "text");
}

function isActiveInside(root) {
  return root.contains(document.activeElement);
}

function valueText(model) {
  return String(model.get("value") ?? "");
}

function syncInputValue(input, value) {
  if (document.activeElement === input) return;
  if (input.value !== value) input.value = value;
}

function syncOptionSelection(select, model, multiple = false) {
  const value = model.get("value");
  Array.from(select.options).forEach((item) => {
    item.selected = multiple
      ? Array.isArray(value) && value.some((entry) => optionKey(entry) === item.value)
      : optionKey(value) === item.value;
  });
}

function syncTagList(root, value) {
  const list = root.querySelector(".anylumino-TagList");
  if (!list) return;
  list.replaceChildren(
    ...value.map((item) => {
      const tag = document.createElement("sp-tag");
      tag.textContent = String(item);
      return tag;
    }),
  );
}

function syncValue(model, root) {
  const kind = String(model.get("control_kind") ?? "text");
  if (["text", "password", "combobox", "date", "color", "search", "int-text", "bounded-int-text", "float-text", "bounded-float-text"].includes(kind)) {
    const input = root.querySelector("sp-textfield, sp-combobox, sp-color-field, sp-search, sp-number-field");
    if (input) syncInputValue(input, valueText(model));
    return;
  }
  if (kind === "time") {
    const input = root.querySelector(".anylumino-TimeInput");
    if (input) syncInputValue(input, normalizeTime(model.get("value")));
    root.querySelector(".anylumino-TimePicker")?._anyluminoSyncTimeSelection?.();
    return;
  }
  if (kind === "datetime") {
    const parts = datetimeParts(model.get("value"));
    const dateInput = root.querySelector(".anylumino-DateTimeFields input[type='date']");
    const timeInput = root.querySelector(".anylumino-DateTimeFields input[type='time']");
    if (dateInput) syncInputValue(dateInput, parts.date);
    if (timeInput) syncInputValue(timeInput, parts.time);
    return;
  }
  if (kind === "textarea") {
    const textarea = root.querySelector("sp-textfield");
    if (textarea) syncInputValue(textarea, valueText(model));
    return;
  }
  if (kind === "dropdown") {
    const picker = root.querySelector("sp-picker");
    if (picker && !isActiveInside(root)) picker.value = optionKey(model.get("value"));
    return;
  }
  if (kind === "select" || kind === "select-multiple") {
    const select = root.querySelector("select.anylumino-NativeSelect");
    if (select && !isActiveInside(root)) syncOptionSelection(select, model, kind === "select-multiple");
    return;
  }
  if (kind === "checkbox" || kind === "switch") {
    const input = root.querySelector("sp-checkbox, sp-switch");
    if (input) input.checked = Boolean(model.get("value"));
    return;
  }
  if (kind === "toggle") {
    const button = root.querySelector("sp-action-button");
    if (button) button.selected = Boolean(model.get("value"));
    return;
  }
  if (kind === "radio") {
    const group = root.querySelector("sp-radio-group");
    if (group) group.value = optionKey(model.get("value"));
    return;
  }
  if (kind === "toggle-buttons") {
    const value = model.get("value");
    root.querySelectorAll(".anylumino-Segment").forEach((button) => {
      button.selected = optionKey(value) === button.dataset.optionValue;
    });
    return;
  }
  if (kind.includes("slider") || kind === "play") {
    const value = model.get("value");
    const slider = root.querySelector("sp-slider");
    if (!slider) return;
    if (Array.isArray(value)) {
      root.querySelectorAll("sp-slider-handle").forEach((handle, index) => {
        handle.value = Number(value[index]);
      });
    } else {
      slider.value = Number(value ?? 0);
    }
    return;
  }
  if (kind === "int-progress" || kind === "float-progress") {
    const progress = root.querySelector("sp-progress-bar");
    if (progress) progress.value = Number(model.get("value") ?? 0) - Number(model.get("min") ?? 0);
    return;
  }
  if (kind === "html" || kind === "output") {
    const node = root.querySelector(".anylumino-Display");
    if (node) node.innerHTML = String(model.get("value") ?? "");
    return;
  }
  if (kind === "badge") {
    const badge = root.querySelector("sp-badge");
    if (badge) {
      badge.textContent = String(model.get("value") ?? labelText(model));
    }
    return;
  }
  if (kind === "meter") {
    const meter = root.querySelector("sp-meter");
    if (meter) {
      meter.progress = Number(model.get("value") ?? 0);
    }
    return;
  }
  if (kind === "link") {
    const link = root.querySelector("sp-link");
    if (link) {
      link.href = String(model.get("href") || model.get("value") || "#");
      link.textContent = labelText(model) || String(model.get("value") || link.href);
    }
    return;
  }
  if (kind === "tags" || kind === "colors" || kind === "ints" || kind === "floats") {
    syncTagList(root, Array.isArray(model.get("value")) ? model.get("value") : []);
    return;
  }
  if (kind === "image" || kind === "audio" || kind === "video") {
    const node = root.querySelector(".anylumino-Media");
    if (node) node.src = String(model.get("value") ?? "");
    return;
  }
  if (kind === "label" || kind === "valid" || kind === "status-light") {
    const node = root.querySelector(".anylumino-Display, sp-status-light");
    if (node) node.textContent = String(model.get("value") ?? "");
  }
}

function syncDisabledState(model, root) {
  const disabled = Boolean(model.get("disabled"));
  root.querySelectorAll("input, textarea, select, button, sp-button, sp-action-button, sp-checkbox, sp-switch, sp-picker, sp-radio-group, sp-slider, sp-textfield, sp-combobox, sp-search, sp-number-field, sp-color-field").forEach((element) => {
    element.disabled = disabled;
  });
}

export default {
  initialize({ model }) {
    return {
      getValue: () => model.get("value"),
      setValue: (value) => updateModel(model, value),
    };
  },

  render({ model, el, signal }) {
    const render = () => {
      el.replaceChildren(renderControl(model));
    };
    const syncModelValue = () => syncValue(model, el);
    const syncDisabled = () => syncDisabledState(model, el);
    const rerender = () => render();
    const structuralAttributes = [
      "control_kind",
      "description",
      "placeholder",
      "options",
      "min",
      "max",
      "step",
      "base",
      "orientation",
      "readout",
      "readout_format",
      "rows",
      "variant",
      "icon",
      "icon_src",
      "icon_size",
      "icons",
      "tooltips",
      "tooltip",
      "allowed_tags",
      "allow_duplicates",
      "ensure_option",
      "concise",
      "indent",
      "accept",
      "multiple",
      "format",
      "width",
      "height",
      "href",
      "html",
      "autoplay",
      "controls",
      "loop",
      "quiet",
      "spectrum_color",
      "spectrum_scale",
      "spectrum_size",
    ];

    render();
    model.on("change:value", syncModelValue);
    model.on("change:index", syncModelValue);
    model.on("change:disabled", syncDisabled);
    structuralAttributes.forEach((name) => model.on(`change:${name}`, rerender));
    signal.addEventListener("abort", () => {
      model.off("change:value", syncModelValue);
      model.off("change:index", syncModelValue);
      model.off("change:disabled", syncDisabled);
      structuralAttributes.forEach((name) => model.off(`change:${name}`, rerender));
    });
  },
};
