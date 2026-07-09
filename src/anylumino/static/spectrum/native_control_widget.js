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

function makeTimeControl(model, onInput) {
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

  const [hourValue = "00", minuteValue = "00"] = (input.value || "00:00").split(":");
  const hour = makeTimeSelect(hourValue, 24);
  const minute = makeTimeSelect(minuteValue, 60);

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
    popup.hidden = !popup.hidden;
  });

  document.addEventListener("click", (event) => {
    if (!group.contains(event.target)) popup.hidden = true;
  });

  group.append(input, button, popup);
  return group;
}

function makeDatetimeControl(model) {
  const group = document.createElement("div");
  group.className = "anylumino-NativeDateTime";

  const dateInput = makeDateInput(model, () => {
    setModelValue(model, `${dateInput.value}T${timePart(model.get("value")) || "00:00"}`);
  });
  const timeInput = makeTimeControl(model, (value) => {
    setModelValue(model, `${dateInput.value || datePart(model.get("value"))}T${value}`);
  });

  group.append(dateInput, timeInput);
  return group;
}

function makeControl(model) {
  const kind = getValue(model, "control_kind", "date");
  if (kind === "datetime") return makeDatetimeControl(model);
  if (kind === "time") return makeTimeControl(model, (value) => setModelValue(model, value));
  return makeDateInput(model, (value) => setModelValue(model, value));
}

export default {
  render({ model, el }) {
    const renderControl = () => {
      el.innerHTML = "";
      const valueControl = makeControl(model);
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

    for (const name of ["control_kind", "description", "disabled", "min", "max", "step", "width"]) {
      model.on(`change:${name}`, renderControl);
    }
    model.on("change:value", syncValue);
  },
};
