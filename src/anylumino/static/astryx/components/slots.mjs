import { Toolbar } from "@astryxdesign/core/Toolbar";
import React from "react";
import { textFor } from "./model.mjs";

export function slotChildren(model) {
  const refs = model.get("widgets") ?? [];
  if (refs.length === 0) {
    return null;
  }
  const keys = model.get("child_keys") ?? [];
  return refs.map((_ref, index) => slotChild(model, keys[index] ?? "", index));
}

export function slotChild(model, key, index, hidden = false) {
  return React.createElement("div", {
    className: "anylumino-AstryxChild",
    "data-anylumino-key": key ?? "",
    "data-anylumino-index": String(index),
    key: `${key ?? "widget"}-${index}`,
    hidden: hidden || undefined,
  });
}

/**
 * Whether a slot belongs to the widget rooted at `rootElement` rather than to
 * one of its mounted children. Children mount inside a slot, so every slot they
 * contribute has one of ours between it and the root.
 */
export function isOwnSlot(slot, rootElement) {
  for (let node = slot.parentElement; node && node !== rootElement; node = node.parentElement) {
    if (node.classList.contains("anylumino-AstryxChild")) {
      return false;
    }
  }
  return true;
}

/**
 * This widget's own slots, keyed by the index they hold. Component DOM order
 * such as Toolbar start, center, and end need not follow key order, so slots are
 * matched by index rather than by document position.
 */
export function ownSlots(model, rootElement) {
  const slots = new Map();
  for (const slot of rootElement.querySelectorAll(".anylumino-AstryxChild")) {
    const index = slot.dataset.anyluminoIndex;
    if (index !== undefined && !slots.has(index) && isOwnSlot(slot, rootElement)) {
      slots.set(index, slot);
    }
  }
  return slots;
}

export function keyedSlotChildren(model) {
  const refs = model.get("widgets") ?? [];
  if (refs.length === 0) {
    return [];
  }
  const keys = model.get("child_keys") ?? [];
  return refs.map((_ref, index) => slotChild(model, keys[index] ?? "", index));
}

export function slotByKey(model, key) {
  const refs = model.get("widgets") ?? [];
  const keys = model.get("child_keys") ?? [];
  const index = keys.indexOf(key);
  if (index < 0 || index >= refs.length) {
    return undefined;
  }
  return slotChild(model, key, index);
}

export function panelChildren(model) {
  const count = (model.get("widgets") ?? []).length;
  const keys = model.get("child_keys") ?? [];
  const titles = model.get("titles") ?? [];
  return {
    count,
    keys: Array.from({ length: count }, (_, index) => String(keys[index] ?? "")),
    titles: Array.from({ length: count }, (_, index) => String(titles[index] || keys[index] || `Item ${index + 1}`)),
  };
}

/** Children of a component that renders its own content: its slots, if any. */
export function slotsOnly({ model }) {
  return slotChildren(model) || undefined;
}

/** Children of a component that shows text without slots. */
export function slotsOrText({ model }) {
  return slotChildren(model) || textFor(model) || undefined;
}
