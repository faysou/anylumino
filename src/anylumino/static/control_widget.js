import "https://esm.sh/@awesome.me/webawesome@3.7.0/dist/components/icon/icon.js?bundle";

function optionParts(option) {
  if (Array.isArray(option) && option.length === 2) {
    return { label: String(option[0]), value: option[1] };
  }
  return { label: String(option), value: option };
}

function optionKey(value) {
  return JSON.stringify(value);
}

function iconSpec(model, source) {
  const raw = typeof source === "object" && source !== null ? source : { name: source };
  const name = String(raw.name ?? raw.icon ?? "").trim();
  if (!name) {
    return null;
  }
  return {
    name,
    family: String(raw.family ?? raw.icon_family ?? model.get("icon_family") ?? "classic"),
    variant: String(raw.variant ?? raw.icon_variant ?? model.get("icon_variant") ?? "solid"),
    library: String(raw.library ?? raw.icon_library ?? model.get("icon_library") ?? "default"),
  };
}

function createIcon(model, source) {
  const spec = iconSpec(model, source);
  if (!spec) {
    return null;
  }
  const icon = document.createElement("wa-icon");
  icon.className = "anylumino-WaIcon";
  icon.name = spec.name;
  icon.family = spec.family;
  icon.variant = spec.variant;
  icon.library = spec.library;
  icon.setAttribute("aria-hidden", "true");
  return icon;
}

function updateModel(model, value) {
  model.set("value", value);
  model.save_changes();
}

function labelText(model) {
  return String(model.get("description") ?? "");
}

function controlShell(model, control) {
  const shell = document.createElement("label");
  shell.className = "anylumino-Control";
  shell.dataset.kind = String(model.get("control_kind") ?? "text");

  const description = labelText(model);
  if (description) {
    const label = document.createElement("span");
    label.className = "anylumino-ControlLabel";
    label.textContent = description;
    shell.append(label);
  }

  shell.append(control);
  return shell;
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

function datetimeLocalValue(value) {
  const text = String(value ?? "");
  if (!text) {
    return "";
  }
  return text
    .replace(" ", "T")
    .replace(/([+-]\d{2}:?\d{2}|Z)$/u, "");
}

function datetimeParts(value) {
  const text = datetimeLocalValue(value);
  const [date = "", time = ""] = text.split("T");
  return {
    date,
    time: time.slice(0, 5),
  };
}

function joinDatetimeParts(date, time) {
  if (!date && !time) {
    return "";
  }
  return `${date || "1970-01-01"}T${time || "00:00"}`;
}

function normalizeTime(value) {
  return String(value ?? "").slice(0, 5);
}

function timeParts(value) {
  const [hour = "00", minute = "00"] = normalizeTime(value).split(":");
  return {
    hour: hour.padStart(2, "0"),
    minute: minute.padStart(2, "0"),
  };
}

function joinTimeParts(hour, minute) {
  return `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}

function inputValue(value, type) {
  if (type === "datetime-local") {
    return datetimeLocalValue(value);
  }
  return String(value ?? "");
}

function makeInput(model, type) {
  const input = document.createElement("input");
  input.className = "anylumino-WaInput";
  input.type = type;
  input.value = inputValue(model.get("value"), type);
  input.placeholder = String(model.get("placeholder") ?? "");
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
  input.className = "anylumino-WaInput anylumino-TimeInput";
  input.type = "time";
  input.value = normalizeTime(value);
  syncDisabled(model, input);

  const button = document.createElement("button");
  button.type = "button";
  button.className = "anylumino-TimePickerButton";
  button.title = "Open time picker";
  button.disabled = Boolean(model.get("disabled"));
  const icon = createIcon(model, "clock");
  if (icon) {
    button.append(icon);
  } else {
    button.textContent = "Time";
  }

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

  const createOption = (value, part) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "anylumino-TimePickerOption";
    item.textContent = value;
    item.dataset.value = value;
    item.dataset.part = part;
    item.addEventListener("click", () => {
      const current = timeParts(input.value);
      input.value = part === "hour" ? joinTimeParts(value, current.minute) : joinTimeParts(current.hour, value);
      onValueChanged(input.value);
      syncSelection();
      if (part === "minute") {
        hidePicker();
      }
      input.focus();
    });
    return item;
  };

  for (let hour = 0; hour < 24; hour += 1) {
    hourColumn.append(createOption(String(hour).padStart(2, "0"), "hour"));
  }
  for (let minute = 0; minute < 60; minute += 1) {
    minuteColumn.append(createOption(String(minute).padStart(2, "0"), "minute"));
  }
  columns.append(hourColumn, minuteColumn);
  popup.append(columns);

  const syncSelection = () => {
    const current = timeParts(input.value);
    popup.querySelectorAll(".anylumino-TimePickerOption").forEach((item) => {
      item.dataset.selected =
        (item.dataset.part === "hour" && item.dataset.value === current.hour) ||
        (item.dataset.part === "minute" && item.dataset.value === current.minute)
          ? "true"
          : "false";
    });
  };
  wrap._anyluminoSyncTimeSelection = syncSelection;
  const positionPopup = () => {
    if (popup.hidden) {
      return;
    }
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
    if (Boolean(model.get("disabled"))) {
      return;
    }
    syncSelection();
    popup.hidden = false;
    positionPopup();
    window.addEventListener("resize", positionPopup);
    document.addEventListener("scroll", positionPopup, true);
    popup.querySelectorAll('.anylumino-TimePickerOption[data-selected="true"]').forEach((selected) => {
      selected.scrollIntoView({ block: "nearest" });
    });
  };
  const togglePicker = () => {
    if (popup.hidden) {
      showPicker();
      return;
    }
    hidePicker();
  };

  const eventName = model.get("continuous_update") ? "input" : "change";
  input.addEventListener(eventName, () => {
    onValueChanged(input.value);
    syncSelection();
  });
  input.addEventListener("click", showPicker);
  input.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      showPicker();
      popup.querySelector('.anylumino-TimePickerOption[data-selected="true"]')?.focus();
    }
    if (event.key === "Escape") {
      hidePicker();
    }
  });
  button.addEventListener("click", (event) => {
    event.preventDefault();
    togglePicker();
  });
  wrap.addEventListener("focusout", (event) => {
    if (
      event.relatedTarget instanceof Node &&
      (wrap.contains(event.relatedTarget) || popup.contains(event.relatedTarget))
    ) {
      return;
    }
    hidePicker();
  });
  popup.addEventListener("focusout", (event) => {
    if (
      event.relatedTarget instanceof Node &&
      (wrap.contains(event.relatedTarget) || popup.contains(event.relatedTarget))
    ) {
      return;
    }
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
  dateInput.className = "anylumino-WaInput";
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
  const textarea = document.createElement("textarea");
  textarea.className = "anylumino-WaInput anylumino-WaTextarea";
  textarea.value = String(model.get("value") ?? "");
  textarea.placeholder = String(model.get("placeholder") ?? "");
  textarea.rows = Number(model.get("rows") ?? 4);
  syncDisabled(model, textarea);

  const eventName = model.get("continuous_update") ? "input" : "change";
  textarea.addEventListener(eventName, () => updateModel(model, textarea.value));
  return controlShell(model, textarea);
}

function makeSelect(model, multiple = false) {
  const select = document.createElement("select");
  select.className = "anylumino-WaInput anylumino-WaSelect";
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
      const selected = Array.from(select.selectedOptions).map((item) => {
        const match = options.find((option) => optionKey(option.value) === item.value);
        return match?.value ?? item.value;
      });
      updateModel(model, selected);
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
  const group = document.createElement("div");
  group.className = "anylumino-ChoiceGroup";
  syncDisabled(model, group);
  const value = model.get("value");

  for (const option of model.get("options") ?? []) {
    const parts = optionParts(option);
    const label = document.createElement("label");
    label.className = "anylumino-Radio";
    const input = document.createElement("input");
    input.type = "radio";
    input.name = model.model_id;
    input.dataset.optionValue = optionKey(parts.value);
    input.checked = optionKey(value) === optionKey(parts.value);
    input.disabled = Boolean(model.get("disabled"));
    input.addEventListener("change", () => updateModel(model, parts.value));
    const text = document.createElement("span");
    text.textContent = parts.label;
    label.append(input, text);
    group.append(label);
  }

  return controlShell(model, group);
}

function makeToggleButtons(model) {
  const group = document.createElement("div");
  group.className = "anylumino-Segmented";
  group.dataset.variant = String(model.get("button_style") || "neutral");
  const value = model.get("value");
  const icons = model.get("icons") ?? [];
  const tooltips = model.get("tooltips") ?? [];

  Array.from(model.get("options") ?? []).forEach((option, index) => {
    const parts = optionParts(option);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "anylumino-Segment";
    button.disabled = Boolean(model.get("disabled"));
    button.dataset.optionValue = optionKey(parts.value);
    button.dataset.selected = optionKey(value) === optionKey(parts.value) ? "true" : "false";
    button.title = String(tooltips[index] ?? "");
    const icon = createIcon(model, icons[index]);
    if (icon) {
      button.append(icon);
    }
    const text = document.createElement("span");
    text.textContent = parts.label;
    button.append(text);
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
  const label = document.createElement("label");
  label.className = toggle ? "anylumino-Toggle" : "anylumino-Checkbox";
  const input = document.createElement("input");
  input.type = "checkbox";
  input.checked = Boolean(model.get("value"));
  input.disabled = Boolean(model.get("disabled"));
  input.addEventListener("change", () => updateModel(model, input.checked));
  const mark = document.createElement("span");
  mark.className = toggle ? "anylumino-ToggleTrack" : "anylumino-CheckboxMark";
  const text = document.createElement("span");
  text.textContent = labelText(model);
  label.append(input, mark, text);
  return label;
}

function makeButton(model, toggle = false) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "anylumino-WaButton";
  button.dataset.variant = String(model.get("button_style") || "neutral");
  button.dataset.pressed = toggle ? String(Boolean(model.get("value"))) : "false";
  button.disabled = Boolean(model.get("disabled"));
  button.title = String(model.get("tooltip") ?? "");

  const icon = createIcon(model, model.get("icon"));
  if (icon) {
    button.append(icon);
  }

  const text = document.createElement("span");
  text.textContent = labelText(model);
  button.append(text);
  button.addEventListener("click", () => {
    if (toggle) {
      updateModel(model, !Boolean(model.get("value")));
    }
    model.send({ type: "click" });
  });
  return button;
}

function makeSlider(model, range = false, log = false) {
  const wrap = document.createElement("div");
  wrap.className = "anylumino-SliderWrap";
  const value = model.get("value");
  const values = range ? [...(Array.isArray(value) ? value : [model.get("min"), model.get("max")])] : [value];

  values.forEach((item, index) => {
    const input = document.createElement("input");
    input.className = "anylumino-WaSlider";
    input.type = "range";
    input.min = String(model.get("min") ?? 0);
    input.max = String(model.get("max") ?? 100);
    input.step = String(model.get("step") ?? 1);
    input.value = String(log ? Math.log(Number(item)) / Math.log(Number(model.get("base") || 10)) : item);
    input.disabled = Boolean(model.get("disabled"));
    input.addEventListener(model.get("continuous_update") ? "input" : "change", () => {
      const next = Number(input.value);
      const denormalized = log ? Math.pow(Number(model.get("base") || 10), next) : next;
      if (!range) {
        updateModel(model, denormalized);
        return;
      }
      const current = Array.isArray(model.get("value")) ? [...model.get("value")] : [...values];
      current[index] = denormalized;
      updateModel(model, current);
    });
    wrap.append(input);
  });

  if (model.get("readout")) {
    const output = document.createElement("output");
    output.className = "anylumino-Readout";
    output.textContent = Array.isArray(value) ? value.join(" - ") : String(value ?? "");
    wrap.append(output);
  }

  return controlShell(model, wrap);
}

function makeSelectionSlider(model, range = false) {
  const options = Array.from(model.get("options") ?? []).map(optionParts);
  const selected = model.get("value");
  const selectedIndex = range
    ? [0, Math.max(options.length - 1, 0)]
    : Math.max(options.findIndex((option) => optionKey(option.value) === optionKey(selected)), 0);

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
  shell.querySelectorAll("input").forEach((input, index) => {
    input.addEventListener("change", () => {
      if (range) {
        const current = Array.from(shell.querySelectorAll("input")).map((item) => options[Number(item.value)]?.value);
        updateModel(model, current);
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
  const progress = document.createElement("progress");
  progress.className = "anylumino-Progress";
  progress.value = Number(model.get("value") ?? 0);
  progress.max = Number(model.get("max") ?? 100) - Number(model.get("min") ?? 0);
  return controlShell(model, progress);
}

function makeTags(model, numeric = null) {
  const wrap = document.createElement("div");
  wrap.className = "anylumino-Tags";
  const list = document.createElement("div");
  list.className = "anylumino-TagList";
  const value = Array.isArray(model.get("value")) ? model.get("value") : [];
  for (const item of value) {
    const tag = document.createElement("span");
    tag.className = "anylumino-Tag";
    tag.textContent = String(item);
    list.append(tag);
  }
  const input = document.createElement("input");
  input.className = "anylumino-WaInput";
  input.placeholder = "Add value";
  input.disabled = Boolean(model.get("disabled"));
  input.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" || !input.value.trim()) {
      return;
    }
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
  const button = makeButton(model);
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
  wrap.append(button, input);
  return wrap;
}

function makeMedia(model, kind) {
  const value = String(model.get("value") ?? "");
  const node = document.createElement(kind);
  node.className = "anylumino-Media";
  if (value) node.src = value;
  node.controls = Boolean(model.get("controls"));
  node.autoplay = Boolean(model.get("autoplay"));
  node.loop = Boolean(model.get("loop"));
  setIfDefined(node, "width", model.get("width"));
  setIfDefined(node, "height", model.get("height"));
  return controlShell(model, node);
}

function makeDisplay(model, html = false) {
  const node = document.createElement("div");
  node.className = "anylumino-Display";
  if (html) {
    node.innerHTML = String(model.get("value") ?? "");
  } else {
    node.textContent = String(model.get("value") ?? "");
  }
  return controlShell(model, node);
}

function renderControl(model) {
  const kind = String(model.get("control_kind") ?? "text");
  if (kind === "textarea") return makeTextarea(model);
  if (kind === "password") return makeInput(model, "password");
  if (kind === "combobox") return makeInput(model, "text");
  if (kind === "dropdown") return makeSelect(model);
  if (kind === "select") return makeSelect(model);
  if (kind === "select-multiple") return makeSelect(model, true);
  if (kind === "radio") return makeRadio(model);
  if (kind === "toggle-buttons") return makeToggleButtons(model);
  if (kind === "button") return makeButton(model);
  if (kind === "checkbox") return makeCheckbox(model);
  if (kind === "toggle") return makeButton(model, true);
  if (kind === "valid") return makeDisplay(model, false);
  if (kind === "int-slider" || kind === "float-slider") return makeSlider(model);
  if (kind === "int-range-slider" || kind === "float-range-slider") return makeSlider(model, true);
  if (kind === "float-log-slider") return makeSlider(model, false, true);
  if (kind === "selection-slider") return makeSelectionSlider(model);
  if (kind === "selection-range-slider") return makeSelectionSlider(model, true);
  if (kind === "int-text" || kind === "bounded-int-text" || kind === "float-text" || kind === "bounded-float-text") {
    return makeInput(model, "number");
  }
  if (kind === "int-progress" || kind === "float-progress") return makeProgress(model);
  if (kind === "play") return makeSlider(model);
  if (kind === "date") return makeInput(model, "date");
  if (kind === "time") return makeTimeInput(model);
  if (kind === "datetime") return makeDatetimeInput(model);
  if (kind === "color") return makeInput(model, "color");
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
  return makeInput(model, "text");
}

function isActiveInside(root) {
  return root.contains(document.activeElement);
}

function valueText(model) {
  return String(model.get("value") ?? "");
}

function browserInputValue(model, kind) {
  return valueText(model);
}

function syncDatetimeValue(model, root) {
  const parts = datetimeParts(model.get("value"));
  const dateInput = root.querySelector(".anylumino-DateTimeFields input[type='date']");
  const timeInput = root.querySelector(".anylumino-DateTimeFields input[type='time']");
  if (dateInput) {
    syncInputValue(dateInput, parts.date);
  }
  if (timeInput) {
    syncInputValue(timeInput, parts.time);
  }
}

function syncTimeValue(model, root) {
  const input = root.querySelector(".anylumino-TimeInput");
  if (input) {
    syncInputValue(input, normalizeTime(model.get("value")));
  }
  root.querySelector(".anylumino-TimePicker")?._anyluminoSyncTimeSelection?.();
}

function syncInputValue(input, value) {
  if (document.activeElement === input) {
    return;
  }
  if (input.value !== value) {
    input.value = value;
  }
}

function syncOptionSelection(select, model, multiple = false) {
  const value = model.get("value");
  Array.from(select.options).forEach((item) => {
    item.selected = multiple
      ? Array.isArray(value) && value.some((entry) => optionKey(entry) === item.value)
      : optionKey(value) === item.value;
  });
}

function sliderValue(model, value, log = false) {
  if (value === undefined || value === null) {
    return "";
  }
  if (!log) {
    return String(value);
  }
  return String(Math.log(Number(value)) / Math.log(Number(model.get("base") || 10)));
}

function syncSliderInputs(root, values, model, log = false) {
  root.querySelectorAll("input.anylumino-WaSlider").forEach((input, index) => {
    syncInputValue(input, sliderValue(model, values[index], log));
  });
}

function syncReadout(root, value) {
  const output = root.querySelector("output.anylumino-Readout");
  if (output) {
    output.textContent = Array.isArray(value) ? value.join(" - ") : String(value ?? "");
  }
}

function syncTagList(root, value) {
  const list = root.querySelector(".anylumino-TagList");
  if (!list) {
    return;
  }
  list.replaceChildren(
    ...value.map((item) => {
      const tag = document.createElement("span");
      tag.className = "anylumino-Tag";
      tag.textContent = String(item);
      return tag;
    }),
  );
}

function syncValue(model, root) {
  const kind = String(model.get("control_kind") ?? "text");

  if (
    [
      "text",
      "password",
      "combobox",
      "date",
      "color",
      "int-text",
      "bounded-int-text",
      "float-text",
      "bounded-float-text",
    ].includes(kind)
  ) {
    const input = root.querySelector("input.anylumino-WaInput");
    if (input) {
      syncInputValue(input, browserInputValue(model, kind));
    }
    return;
  }

  if (kind === "time") {
    syncTimeValue(model, root);
    return;
  }

  if (kind === "datetime") {
    syncDatetimeValue(model, root);
    return;
  }

  if (kind === "textarea") {
    const textarea = root.querySelector("textarea.anylumino-WaTextarea");
    if (textarea) {
      syncInputValue(textarea, valueText(model));
    }
    return;
  }

  if (kind === "dropdown" || kind === "select") {
    const select = root.querySelector("select.anylumino-WaSelect");
    if (select && !isActiveInside(root)) {
      syncOptionSelection(select, model);
    }
    return;
  }

  if (kind === "select-multiple") {
    const select = root.querySelector("select.anylumino-WaSelect");
    if (select && !isActiveInside(root)) {
      syncOptionSelection(select, model, true);
    }
    return;
  }

  if (kind === "checkbox") {
    const input = root.querySelector("input[type='checkbox']");
    if (input) {
      input.checked = Boolean(model.get("value"));
    }
    return;
  }

  if (kind === "toggle") {
    const button = root.querySelector("button.anylumino-WaButton");
    if (button) {
      button.dataset.pressed = String(Boolean(model.get("value")));
    }
    return;
  }

  if (kind === "radio") {
    const value = model.get("value");
    root.querySelectorAll("input[type='radio']").forEach((input) => {
      input.checked = optionKey(value) === input.dataset.optionValue;
    });
    return;
  }

  if (kind === "toggle-buttons") {
    const value = model.get("value");
    root.querySelectorAll(".anylumino-Segment").forEach((button) => {
      button.dataset.selected = optionKey(value) === button.dataset.optionValue ? "true" : "false";
    });
    return;
  }

  if (
    kind === "int-slider" ||
    kind === "float-slider" ||
    kind === "float-log-slider" ||
    kind === "play" ||
    kind === "int-range-slider" ||
    kind === "float-range-slider"
  ) {
    const value = model.get("value");
    const values = Array.isArray(value) ? value : [value];
    const log = kind === "float-log-slider";
    syncSliderInputs(root, values, model, log);
    syncReadout(root, value);
    return;
  }

  if (kind === "selection-slider" || kind === "selection-range-slider") {
    const options = Array.from(model.get("options") ?? []).map(optionParts);
    const value = model.get("value");
    const values = Array.isArray(value) ? value : [value];
    const indexes = values.map((item) =>
      Math.max(
        options.findIndex((option) => optionKey(option.value) === optionKey(item)),
        0,
      ),
    );
    syncSliderInputs(root, indexes, model);
    syncReadout(root, value);
    return;
  }

  if (kind === "int-progress" || kind === "float-progress") {
    const progress = root.querySelector("progress.anylumino-Progress");
    if (progress) {
      progress.value = Number(model.get("value") ?? 0);
    }
    return;
  }

  if (kind === "html" || kind === "output") {
    const node = root.querySelector(".anylumino-Display");
    if (node) {
      node.innerHTML = String(model.get("value") ?? "");
    }
    return;
  }

  if (kind === "tags" || kind === "colors" || kind === "ints" || kind === "floats") {
    const value = Array.isArray(model.get("value")) ? model.get("value") : [];
    syncTagList(root, value);
    return;
  }

  if (kind === "image" || kind === "audio" || kind === "video") {
    const node = root.querySelector(".anylumino-Media");
    if (node) {
      node.src = String(model.get("value") ?? "");
    }
  }

  if (kind === "label" || kind === "valid") {
    const node = root.querySelector(".anylumino-Display");
    if (node) {
      node.textContent = String(model.get("value") ?? "");
    }
  }
}

function syncDisabledState(model, root) {
  const disabled = Boolean(model.get("disabled"));
  root.querySelectorAll("input, textarea, select, button").forEach((element) => {
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
      "button_style",
      "icon",
      "icon_family",
      "icon_variant",
      "icon_library",
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
      "html",
      "autoplay",
      "controls",
      "loop",
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
