import "@spectrum-web-components/theme/sp-theme.js";
import "@spectrum-web-components/theme/theme-light.js";
import "@spectrum-web-components/theme/theme-dark.js";
import "@spectrum-web-components/theme/scale-medium.js";
import "@spectrum-web-components/icon/sp-icon.js";
import "@spectrum-web-components/action-button/sp-action-button.js";
import "@spectrum-web-components/button/sp-button.js";
import "@spectrum-web-components/color-handle/sp-color-handle.js";
import "@spectrum-web-components/color-loupe/sp-color-loupe.js";
import "@spectrum-web-components/field-group/sp-field-group.js";
import "@spectrum-web-components/help-text/sp-help-text.js";
import "@spectrum-web-components/infield-button/sp-infield-button.js";
import "@spectrum-web-components/overlay/sp-overlay.js";
import "@spectrum-web-components/picker-button/sp-picker-button.js";
import "@spectrum-web-components/popover/sp-popover.js";
import "@spectrum-web-components/progress-circle/sp-progress-circle.js";
import "@spectrum-web-components/table/elements.js";
import "@spectrum-web-components/tooltip/sp-tooltip.js";
import "@spectrum-web-components/tray/sp-tray.js";
import "@spectrum-web-components/underlay/sp-underlay.js";
import "@spectrum-web-components/icons-ui/icons/sp-icon-checkmark100.js";
import "@spectrum-web-components/icons-ui/icons/sp-icon-chevron100.js";
import "@spectrum-web-components/icons-ui/icons/sp-icon-cross100.js";
import "./spectrum_icons.js";
import {
  combineSignals,
  cssSize,
  removeModelListener,
  renderWidgetRef,
} from "./composition.js";

function setBoolAttribute(element, name, value) {
  if (Boolean(value)) {
    element.setAttribute(name, "");
  } else {
    element.removeAttribute(name);
  }
}

function setIfDefined(element, name, value) {
  if (value === undefined || value === null || value === "") {
    element.removeAttribute(name);
    return;
  }
  element.setAttribute(name, String(value));
}

function applyAttributes(element, attributes) {
  for (const [name, value] of Object.entries(attributes ?? {})) {
    if (name === "class" || name === "className") {
      element.classList.add(...String(value).split(/\s+/u).filter(Boolean));
      continue;
    }
    if (typeof value === "boolean") {
      setBoolAttribute(element, name, value);
    } else {
      setIfDefined(element, name, value);
    }
  }
}

function workflowIconName(rawName) {
  const name = String(rawName ?? "").trim();
  const aliases = {
    "check": "CheckmarkCircle",
    "chevron": "ChevronDown",
    "close": "Close",
    "cross": "Close",
    "dismiss": "Close",
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

function createWorkflowIcon(model, fallback = "") {
  const src = String(model.get("icon_src") ?? "").trim();
  if (src) {
    const icon = document.createElement("sp-icon");
    icon.className = "anylumino-SpectrumWidgetIcon";
    icon.src = src;
    icon.size = String(model.get("icon_size") ?? "s");
    icon.slot = "icon";
    return icon;
  }

  const name = workflowIconName(model.get("icon") || fallback);
  if (!name) {
    return null;
  }
  const icon = document.createElement(`sp-icon-${kebabName(name)}`);
  icon.className = "anylumino-SpectrumWidgetIcon";
  icon.size = String(model.get("icon_size") ?? "s");
  icon.slot = "icon";
  return icon;
}

function createFallbackUiIcon(model, fallback = "") {
  const normalized = workflowIconName(fallback);
  const uiIcons = {
    Checkmark: "sp-icon-checkmark100",
    CheckmarkCircle: "sp-icon-checkmark100",
    ChevronDown: "sp-icon-chevron100",
    Close: "sp-icon-cross100",
  };
  const tagName = uiIcons[normalized];
  if (!tagName) {
    return createWorkflowIcon(model, fallback);
  }

  const icon = document.createElement(tagName);
  icon.className = "anylumino-SpectrumWidgetIcon";
  icon.size = String(model.get("icon_size") ?? "s");
  icon.slot = "icon";
  return icon;
}

function createButtonIcon(model, fallback = "") {
  if (model.get("icon") || model.get("icon_src")) {
    return createWorkflowIcon(model, fallback);
  }
  return createFallbackUiIcon(model, fallback);
}

function createUiIcon(model) {
  const value = String(model.get("value") || "checkmark100").replace(/[^a-zA-Z0-9_-]/g, "");
  const icon = document.createElement(`sp-icon-${kebabName(value)}`);
  icon.className = "anylumino-SpectrumWidgetIcon";
  if (model.get("label")) {
    icon.label = String(model.get("label"));
  } else {
    icon.setAttribute("aria-hidden", "true");
  }
  return icon;
}

function themeFor(child, model) {
  const theme = document.createElement("sp-theme");
  theme.className = "anylumino-SpectrumWidgetTheme";
  theme.color = String(model.get("spectrum_color") ?? "light");
  theme.scale = String(model.get("spectrum_scale") ?? "medium");
  theme.append(child);
  return theme;
}

function textFor(model) {
  return String(model.get("text") || model.get("label") || model.get("value") || "");
}

function buttonElement(model, tagName, fallbackIcon) {
  const button = document.createElement(tagName);
  button.className = `anylumino-SpectrumWidgetButton anylumino-${model.get("component_kind")}`;
  button.disabled = Boolean(model.get("disabled"));
  button.label = String(model.get("label") || textFor(model) || fallbackIcon);
  button.size = String(model.get("spectrum_size") ?? "m");
  setIfDefined(button, "variant", model.get("variant"));
  const icon = createButtonIcon(model, fallbackIcon);
  if (icon) {
    button.append(icon);
  }
  const text = textFor(model);
  if (text && model.get("component_kind") !== "close-button" && model.get("component_kind") !== "clear-button") {
    button.append(document.createTextNode(text));
  }
  button.addEventListener("click", () => model.send({ type: "click" }));
  return button;
}

function basicElement(model, tagName) {
  const element = document.createElement(tagName);
  element.className = `anylumino-SpectrumComponent anylumino-${model.get("component_kind")}`;
  setIfDefined(element, "size", model.get("spectrum_size"));
  setIfDefined(element, "variant", model.get("variant"));
  setIfDefined(element, "placement", model.get("placement"));
  setIfDefined(element, "label", model.get("label"));
  setBoolAttribute(element, "open", model.get("is_open"));
  setBoolAttribute(element, "disabled", model.get("disabled"));
  setBoolAttribute(element, "selected", model.get("selected"));
  setBoolAttribute(element, "indeterminate", model.get("indeterminate"));
  applyAttributes(element, model.get("attributes"));
  if (model.get("text")) {
    element.textContent = String(model.get("text"));
  }
  return element;
}

function slottedContainer(model, tagName, slotRoot = null) {
  const element = basicElement(model, tagName);
  const root = slotRoot ?? element;
  root.classList.add("anylumino-SpectrumSlots");
  return { element, root };
}

function createDialog(model) {
  const wrap = document.createElement("div");
  wrap.className = "anylumino-Dialog";
  wrap.hidden = !model.get("is_open");

  const underlay = document.createElement("sp-underlay");
  underlay.className = "anylumino-DialogUnderlay";
  underlay.open = Boolean(model.get("is_open"));

  const panel = document.createElement("div");
  panel.className = "anylumino-DialogPanel";
  panel.role = "dialog";
  panel.ariaModal = "true";
  panel.style.width = cssSize(model.get("width"), "420px");
  panel.style.height = cssSize(model.get("height"), "auto");

  const header = document.createElement("div");
  header.className = "anylumino-DialogHeader";
  const title = document.createElement("div");
  title.className = "anylumino-DialogTitle";
  title.textContent = String(model.get("label") ?? "");
  const close = buttonElement(model, "sp-action-button", "Close");
  close.classList.add("anylumino-DialogClose");
  close.addEventListener("click", () => {
    model.set("is_open", false);
    model.save_changes();
    model.send({ type: "close" });
  });
  header.append(title, close);

  const body = document.createElement("div");
  body.className = "anylumino-DialogBody anylumino-SpectrumSlots";
  panel.append(header, body);
  wrap.append(underlay, panel);
  return { element: wrap, root: body };
}

function normalizedTableText(value) {
  if (value === undefined || value === null) {
    return "";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

function compareTableValues(direction, left, right) {
  const leftNumber = Number(left);
  const rightNumber = Number(right);
  const order = direction === "desc" ? -1 : 1;
  if (Number.isFinite(leftNumber) && Number.isFinite(rightNumber)) {
    return (leftNumber - rightNumber) * order;
  }
  return normalizedTableText(left).localeCompare(normalizedTableText(right), undefined, {
    numeric: true,
    sensitivity: "base",
  }) * order;
}

function sortedTableRows(model) {
  const rows = [...(model.get("rows") ?? [])];
  const sortKey = String(model.get("sort_key") ?? "");
  const sortDirection = String(model.get("sort_direction") ?? "");
  if (!sortKey || !["asc", "desc"].includes(sortDirection)) {
    return rows;
  }
  return rows.sort((left, right) =>
    compareTableValues(sortDirection, left?.cells?.[sortKey], right?.cells?.[sortKey]),
  );
}

function createTable(model) {
  const table = document.createElement("sp-table");
  table.className = "anylumino-SpectrumTable";
  table.size = String(model.get("spectrum_size") ?? "m");
  table.selected = [...(model.get("selected") ?? [])].map(String);
  table.selectAllLabel = String(model.get("select_all_label") ?? "Select all rows");
  setIfDefined(table, "selects", model.get("selects"));
  setIfDefined(table, "density", model.get("density"));
  setBoolAttribute(table, "quiet", model.get("quiet"));
  setBoolAttribute(table, "emphasized", model.get("emphasized"));

  const head = document.createElement("sp-table-head");
  for (const column of model.get("columns") ?? []) {
    const cell = document.createElement("sp-table-head-cell");
    cell.textContent = String(column.label ?? column.key ?? "");
    cell.sortKey = String(column.key ?? "");
    cell.sortable = Boolean(model.get("sortable") || column.sortable);
    if (cell.sortKey && cell.sortKey === model.get("sort_key")) {
      setIfDefined(cell, "sort-direction", model.get("sort_direction"));
    }
    if (column.align) {
      cell.style.textAlign = String(column.align);
    }
    head.append(cell);
  }

  const body = document.createElement("sp-table-body");
  const columns = model.get("columns") ?? [];
  for (const rowData of sortedTableRows(model)) {
    const row = document.createElement("sp-table-row");
    row.value = String(rowData.value ?? "");
    for (const column of columns) {
      const cell = document.createElement("sp-table-cell");
      cell.textContent = normalizedTableText(rowData.cells?.[column.key]);
      if (column.align) {
        cell.style.textAlign = String(column.align);
      }
      row.append(cell);
    }
    body.append(row);
  }

  table.addEventListener("change", () => {
    const selected = [...(table.selected ?? [])].map(String);
    model.set("selected", selected);
    model.save_changes();
    model.send({ type: "selection", selected });
  });
  table.addEventListener("sorted", (event) => {
    const sortKey = String(event.detail?.sortKey ?? "");
    const sortDirection = String(event.detail?.sortDirection ?? "");
    model.set("sort_key", sortKey);
    model.set("sort_direction", sortDirection);
    model.save_changes();
    model.send({ type: "sort", sort_key: sortKey, sort_direction: sortDirection });
  });

  table.append(head, body);
  return { element: table };
}

function createComponent(model) {
  const kind = String(model.get("component_kind") ?? "element");

  if (kind === "table") {
    return createTable(model);
  }
  if (kind === "element") {
    return slottedContainer(model, model.get("tag") || "div");
  }
  if (kind === "icon") {
    return { element: createWorkflowIcon(model) ?? document.createElement("span") };
  }
  if (kind === "ui-icon") {
    return { element: createUiIcon(model) };
  }
  if (kind === "clear-button") {
    return { element: buttonElement(model, "sp-action-button", "Close") };
  }
  if (kind === "close-button") {
    return { element: buttonElement(model, "sp-action-button", "Close") };
  }
  if (kind === "infield-button") {
    return { element: buttonElement(model, "sp-infield-button", "ChevronDown") };
  }
  if (kind === "picker-button") {
    return { element: buttonElement(model, "sp-picker-button", "ChevronDown") };
  }
  if (kind === "field-group") {
    const result = slottedContainer(model, "sp-field-group");
    result.element.vertical = model.get("orientation") === "vertical";
    return result;
  }
  if (kind === "help-text") {
    return { element: basicElement(model, "sp-help-text") };
  }
  if (kind === "progress-circle") {
    const element = basicElement(model, "sp-progress-circle");
    element.progress = Number(model.get("value") ?? 0);
    return { element };
  }
  if (kind === "color-handle") {
    const element = basicElement(model, "sp-color-handle");
    element.color = String(model.get("value") ?? "#1473e6");
    return { element };
  }
  if (kind === "color-loupe") {
    const element = basicElement(model, "sp-color-loupe");
    element.color = String(model.get("value") ?? "#1473e6");
    return { element };
  }
  if (kind === "opacity-checkerboard") {
    const element = document.createElement("div");
    element.className = "anylumino-OpacityCheckerboard";
    element.style.width = cssSize(model.get("width"), "120px");
    element.style.height = cssSize(model.get("height"), "48px");
    return { element };
  }
  if (kind === "popover") {
    return slottedContainer(model, "sp-popover");
  }
  if (kind === "tooltip") {
    const wrap = document.createElement("div");
    wrap.className = "anylumino-TooltipWrap";
    const trigger = document.createElement("div");
    trigger.className = "anylumino-TooltipTrigger anylumino-SpectrumSlots";
    const tooltip = basicElement(model, "sp-tooltip");
    tooltip.textContent = String(model.get("text") ?? "");
    wrap.append(trigger, tooltip);
    return { element: wrap, root: trigger };
  }
  if (kind === "tray") {
    return slottedContainer(model, "sp-tray");
  }
  if (kind === "underlay") {
    return { element: basicElement(model, "sp-underlay") };
  }
  if (kind === "overlay") {
    return slottedContainer(model, "sp-overlay");
  }
  if (kind === "dialog") {
    return createDialog(model);
  }

  return slottedContainer(model, model.get("tag") || "div");
}

export default {
  initialize({ model }) {
    return {
      getComponentKind: () => model.get("component_kind"),
    };
  },

  async render({ model, el, signal, host }) {
    if (!host?.getWidget && (model.get("widgets") ?? []).length > 0) {
      throw new Error("[anylumino] The current anywidget host does not support widget composition.");
    }

    let childController = new AbortController();

    const renderCurrent = async () => {
      childController.abort();
      childController = new AbortController();

      const { element, root = element } = createComponent(model);
      const outer = document.createElement("div");
      outer.className = `anylumino-SpectrumWidgetHost anylumino-${model.get("component_kind")}Host`;
      outer.style.width = cssSize(model.get("width"), "");
      outer.style.height = cssSize(model.get("height"), "");
      outer.append(element);
      el.replaceChildren(themeFor(outer, model));

      const refs = model.get("widgets") ?? [];
      const keys = model.get("child_keys") ?? [];
      for (const [index, ref] of refs.entries()) {
        const slot = document.createElement("div");
        slot.className = "anylumino-SpectrumChild";
        slot.dataset.anyluminoKey = keys[index] ?? "";
        root.append(slot);
        await renderWidgetRef(model, host, ref, slot, combineSignals(signal, childController.signal));
      }
    };

    const rerender = () => {
      void renderCurrent();
    };

    const watched = [
      "component_kind",
      "tag",
      "widgets",
      "child_keys",
      "text",
      "label",
      "value",
      "is_open",
      "disabled",
      "selected",
      "indeterminate",
      "variant",
      "placement",
      "orientation",
      "width",
      "height",
      "icon",
      "icon_src",
      "icon_size",
      "spectrum_color",
      "spectrum_scale",
      "spectrum_size",
      "attributes",
      "columns",
      "rows",
      "selected",
      "selects",
      "sort_key",
      "sort_direction",
      "sortable",
      "quiet",
      "emphasized",
      "density",
      "select_all_label",
    ];
    watched.forEach((name) => model.on(`change:${name}`, rerender));
    signal.addEventListener(
      "abort",
      () => {
        childController.abort();
        watched.forEach((name) => removeModelListener(model, `change:${name}`, rerender));
      },
      { once: true },
    );
    await renderCurrent();
  },
};
