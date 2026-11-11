import { combineSignals, modelListeners } from "../layout/composition.js";

function getValue(model, name, fallback = "") {
  const value = model.get(name);
  return value == null ? fallback : value;
}

function setModelValue(model, value) {
  model.set("value", value === "" ? null : value);
  model.save_changes();
}

function datePart(value) {
  if (!value) return "";
  return String(value).split("T")[0];
}

function timePart(value) {
  if (!value) return "";
  const text = String(value);
  const valuePart = text.includes("T") ? text.split("T")[1] : text;
  return valuePart.slice(0, 5);
}

/**
 * The datetime value for a `date` and an `HH:MM` `time` from the inputs, or
 * `null` unless both are set. The seconds of `previous` are kept while its
 * hour and minute match `time`, since the time input shows minutes only.
 */
export function composeDatetime(date, time, previous) {
  if (!date || !time) return null;
  const previousTime = previous && String(previous).includes("T") ? String(previous).split("T")[1] : "";
  return `${date}T${previousTime.startsWith(time) ? previousTime : time}`;
}

function padded(value) {
  return String(value).padStart(2, "0");
}

function applyRange(input, model, transform = (value) => value) {
  for (const name of ["min", "max", "step"]) {
    const value = transform(model.get(name));
    if (value == null || value === "") input.removeAttribute(name);
    else input.setAttribute(name, String(value));
  }
}

function makeShell(model, control) {
  const shell = document.createElement("label");
  shell.className = "anylumino-NativeControl";

  const width = getValue(model, "width");
  if (width) shell.style.width = width;

  const description = getValue(model, "description");
  if (description) {
    const label = document.createElement("span");
    label.className = "anylumino-NativeLabel";
    label.textContent = description;
    shell.append(label);
  }

  shell.append(control);
  return shell;
}

function makeDateInput(model, onInput) {
  const input = document.createElement("input");
  input.className = "anylumino-NativeInput anylumino-NativeDateInput";
  input.type = "date";
  input.value = datePart(model.get("value"));
  input.disabled = Boolean(model.get("disabled"));
  applyRange(input, model, (value) => (value == null ? value : datePart(value)));
  const eventName = model.get("continuous_update") ? "input" : "change";
  input.addEventListener(eventName, () => onInput(input.value));
  return input;
}

function makeTimeSelect(value, count) {
  const select = document.createElement("select");
  select.className = "anylumino-NativeTimeSelect";
  for (let index = 0; index < count; index += 1) {
    const option = document.createElement("option");
    option.value = padded(index);
    option.textContent = padded(index);
    select.append(option);
  }
  select.value = value;
  return select;
}

function makeTimeControl(model, onInput, signal) {
  const group = document.createElement("div");
  group.className = "anylumino-NativeTime";

  const input = document.createElement("input");
  input.className = "anylumino-NativeInput anylumino-NativeTimeInput";
  input.type = "time";
  input.value = timePart(model.get("value"));
  input.disabled = Boolean(model.get("disabled"));
  applyRange(input, model, (value) => (value == null || value === "any" ? value : timePart(value)));
  const eventName = model.get("continuous_update") ? "input" : "change";
  input.addEventListener(eventName, () => onInput(input.value));

  const button = document.createElement("button");
  button.type = "button";
  button.className = "anylumino-NativeTimeButton";
  button.textContent = "Pick";
  button.disabled = input.disabled;

  const popup = document.createElement("div");
  popup.className = "anylumino-NativeTimePopup";
  popup.hidden = true;

  const hour = makeTimeSelect("00", 24);
  const minute = makeTimeSelect("00", 60);
  // The selects start from the value shown when the popup opens, which Python or typing
  // may have changed.
  const showCurrentTime = () => {
    const [hourValue = "00", minuteValue = "00"] = (input.value || "00:00").split(":");
    hour.value = hourValue;
    minute.value = minuteValue;
  };
  showCurrentTime();

  const commit = () => {
    input.value = `${hour.value}:${minute.value}`;
    onInput(input.value);
  };

  hour.addEventListener("change", commit);
  minute.addEventListener("change", commit);

  const hourLabel = document.createElement("span");
  hourLabel.textContent = "Hour";
  const minuteLabel = document.createElement("span");
  minuteLabel.textContent = "Minute";

  popup.append(hourLabel, hour, minuteLabel, minute);
  button.addEventListener("click", (event) => {
    event.preventDefault();
    if (popup.hidden) showCurrentTime();
    popup.hidden = !popup.hidden;
  });

  document.addEventListener(
    "click",
    (event) => {
      if (!group.contains(event.target)) popup.hidden = true;
    },
    { signal },
  );

  group.append(input, button, popup);
  return group;
}

function makeDatetimeControl(model, signal) {
  const group = document.createElement("div");
  group.className = "anylumino-NativeDateTime";

  let timeInput = null;
  const sync = () => setModelValue(model, composeDatetime(dateInput.value, timeInput.querySelector("input").value, model.get("value")));
  const dateInput = makeDateInput(model, sync);
  timeInput = makeTimeControl(model, sync, signal);

  group.append(dateInput, timeInput);
  return group;
}

function makeControl(model, signal) {
  const kind = getValue(model, "control_kind", "date");
  if (kind === "datetime") return makeDatetimeControl(model, signal);
  if (kind === "time") return makeTimeControl(model, (value) => setModelValue(model, value), signal);
  return makeDateInput(model, (value) => setModelValue(model, value));
}

export default {
  render({ model, el, signal }) {
    // Each rebuild drops the document listeners of the controls it replaces.
    let controlController = new AbortController();

    const renderControl = () => {
      controlController.abort();
      controlController = new AbortController();
      el.innerHTML = "";
      const controlSignal = signal ? combineSignals(signal, controlController.signal) : controlController.signal;
      const valueControl = makeControl(model, controlSignal);
      el.append(makeShell(model, valueControl));
    };

    const syncValue = () => {
      const value = model.get("value");
      for (const input of el.querySelectorAll(".anylumino-NativeDateInput")) {
        if (document.activeElement !== input) input.value = datePart(value);
      }
      for (const input of el.querySelectorAll(".anylumino-NativeTimeInput")) {
        if (document.activeElement !== input) input.value = timePart(value);
      }
    };

    renderControl();

    const unbind = modelListeners(model, [
      ...["control_kind", "description", "disabled", "min", "max", "step", "width", "continuous_update"].map((name) => [
        name,
        renderControl,
      ]),
      ["value", syncValue],
    ]);
    signal?.addEventListener(
      "abort",
      () => {
        controlController.abort();
        unbind();
      },
      { once: true },
    );
  },
};
