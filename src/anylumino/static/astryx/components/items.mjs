import { Icon } from "@astryxdesign/core/Icon";
import { NavHeadingMenu, NavHeadingMenuItem } from "@astryxdesign/core/NavMenu";
import { SideNavItem, SideNavSection } from "@astryxdesign/core/SideNav";
import React from "react";
import { sendModelAction } from "../astryx_bridge.mjs";
import { asArray, setStringValue } from "./model.mjs";

export function iconNode(icon, props = {}) {
  if (!icon) {
    return undefined;
  }
  if (typeof icon === "string") {
    return React.createElement(Icon, { icon, ...props });
  }
  return icon;
}

export function itemLabel(item, fallback) {
  if (item && typeof item === "object") {
    return String(item.label ?? item.value ?? fallback);
  }
  return String(item ?? fallback);
}

export function itemValue(item, fallback) {
  if (item && typeof item === "object") {
    return String(item.value ?? item.label ?? fallback);
  }
  return String(item ?? fallback);
}

export function menuItems(model, items) {
  return asArray(items).map((item, index) => {
    if (item?.type === "divider") {
      return { type: "divider" };
    }
    if (item?.type === "section") {
      return {
        ...item,
        items: menuItems(model, item.items),
      };
    }
    const value = itemValue(item, index);
    return {
      ...item,
      label: itemLabel(item, `Action ${index + 1}`),
      isDisabled: Boolean(item?.disabled ?? item?.isDisabled),
      onClick: () => sendModelAction(model, value),
    };
  });
}

export function navHeadingMenu(model, entries) {
  if (!entries?.length) {
    return undefined;
  }
  return React.createElement(
    NavHeadingMenu,
    null,
    entries.map((entry, index) =>
      React.createElement(NavHeadingMenuItem, {
        key: itemValue(entry, index),
        label: itemLabel(entry, `Action ${index + 1}`),
        description: entry?.description,
        isDisabled: Boolean(entry?.disabled),
        onClick: () => sendModelAction(model, itemValue(entry, index)),
      }),
    ),
  );
}

export function sideNavItems(model, items, selected) {
  return asArray(items).map((item, index) => {
    if (item?.type === "section") {
      return React.createElement(
        SideNavSection,
        { key: `section-${index}`, title: String(item.title ?? item.label ?? "") },
        sideNavItems(model, item.items, selected),
      );
    }
    const value = itemValue(item, index);
    return React.createElement(
      SideNavItem,
      {
        key: value,
        label: itemLabel(item, `Item ${index + 1}`),
        icon: iconNode(item?.icon),
        isSelected: value === selected,
        isDisabled: Boolean(item?.disabled),
        onClick: () => setStringValue(model, value),
      },
      item?.items ? sideNavItems(model, item.items, selected) : undefined,
    );
  });
}
