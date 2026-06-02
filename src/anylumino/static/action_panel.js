import {
  CommandPalette,
  Menu,
  MenuBar,
  Panel,
  Widget,
} from "@lumino/widgets";
import { CommandRegistry } from "@lumino/commands";
import "@spectrum-web-components/theme/sp-theme.js";
import "@spectrum-web-components/theme/theme-light.js";
import "@spectrum-web-components/theme/scale-medium.js";
import "@spectrum-web-components/action-button/sp-action-button.js";
import "@spectrum-web-components/icon/sp-icon.js";
import "./spectrum_icons.js";

function cssSize(value, fallback) {
  if (typeof value === "string" && value.trim()) {
    return value;
  }
  return fallback;
}

function removeModelListener(model, eventName, callback) {
  try {
    model.off(eventName, callback);
  } catch {
    model.off(eventName, callback, null);
  }
}

function actionId(action) {
  return String(action?.id ?? action?.label ?? "");
}

function actionLabel(action) {
  return String(action?.label ?? action?.id ?? "");
}

function actionIconClass(action) {
  const id = actionId(action).replace(/[^a-zA-Z0-9_-]/g, "_");
  return iconSpec(action) ? `anylumino-CommandIcon-${id}` : "";
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
  };
  if (aliases[name]) {
    return aliases[name];
  }
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

function iconSpec(action) {
  const name = String(action?.icon ?? "").trim();
  const src = String(action?.icon_src ?? "").trim();
  if (!name && !src) {
    return null;
  }
  return {
    name: workflowIconName(name),
    src,
    size: String(action?.icon_size ?? "s"),
    label: String(action?.icon_label ?? ""),
  };
}

function createIcon(action) {
  const spec = iconSpec(action);
  if (!spec) {
    return null;
  }
  if (spec.src) {
    const icon = document.createElement("sp-icon");
    icon.className = "anylumino-ToolbarIcon";
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
  icon.className = "anylumino-ToolbarIcon";
  icon.size = spec.size;
  icon.slot = "icon";
  if (spec.label) {
    icon.label = spec.label;
  } else {
    icon.setAttribute("aria-hidden", "true");
  }
  return icon;
}

function flattenActions(actions) {
  const flat = [];
  for (const action of actions ?? []) {
    if (Array.isArray(action.items)) {
      flat.push(...action.items);
    } else {
      flat.push(action);
    }
  }
  return flat.filter((action) => actionId(action));
}

function addCommands(commands, actions, activate) {
  for (const action of flattenActions(actions)) {
    const id = actionId(action);
    if (commands.hasCommand(id)) {
      continue;
    }
    commands.addCommand(id, {
      label: actionLabel(action),
      caption: String(action?.caption ?? actionLabel(action)),
      iconClass: actionIconClass(action),
      isEnabled: () => !action.disabled,
      execute: () => activate(id),
    });
  }
}

function decorateCommandIcons(actions) {
  const iconActions = flattenActions(actions).filter((action) => iconSpec(action));
  if (iconActions.length === 0) {
    return null;
  }

  const decorate = () => {
    for (const action of iconActions) {
      const className = actionIconClass(action);
      if (!className) {
        continue;
      }
      document.querySelectorAll(`.${className}`).forEach((node) => {
        if (node.dataset.anyluminoIcon === "true") {
          return;
        }
        const icon = createIcon(action);
        if (icon) {
          node.replaceChildren(icon);
          node.dataset.anyluminoIcon = "true";
        }
      });
    }
  };

  const observer = new MutationObserver(decorate);
  observer.observe(document.body, { childList: true, subtree: true });
  decorate();
  return observer;
}

function createToolbar(model, activate) {
  const panel = new Panel();
  panel.addClass("anylumino-Toolbar");
  for (const action of model.get("actions") ?? []) {
    const id = actionId(action);
    const button = document.createElement("sp-action-button");
    button.className = "anylumino-ToolbarButton";
    button.dataset.actionId = id;
    button.disabled = Boolean(action.disabled);
    button.title = String(action.tooltip ?? action.caption ?? actionLabel(action));
    button.label = actionLabel(action);
    button.size = String(action.size ?? "s");
    if (action.quiet ?? true) {
      button.setAttribute("quiet", "");
    }

    const icon = createIcon(action);
    if (icon) {
      button.classList.add("anylumino-ToolbarButtonIconOnly");
      button.appendChild(icon);
    } else {
      button.textContent = actionLabel(action);
    }
    button.addEventListener("click", () => activate(id));
    panel.node.appendChild(button);
  }
  return panel;
}

function createMenuBar(model, activate) {
  const commands = new CommandRegistry();
  const actions = model.get("actions") ?? [];
  addCommands(commands, actions, activate);

  const bar = new MenuBar();
  bar.addClass("anylumino-MenuBar");

  for (const menuSpec of actions) {
    const menu = new Menu({ commands });
    menu.title.label = String(menuSpec.label ?? "Menu");
    for (const item of menuSpec.items ?? []) {
      if (item.type === "separator") {
        menu.addItem({ type: "separator" });
      } else {
        menu.addItem({ command: actionId(item) });
      }
    }
    bar.addMenu(menu);
  }
  return bar;
}

function createCommandPalette(model, activate) {
  const commands = new CommandRegistry();
  const actions = model.get("actions") ?? [];
  addCommands(commands, actions, activate);

  const palette = new CommandPalette({ commands });
  palette.addClass("anylumino-CommandPalette");
  for (const action of flattenActions(actions)) {
    palette.addItem({
      command: actionId(action),
      category: String(action.category ?? "Commands"),
    });
  }
  return palette;
}

export default {
  initialize({ model }) {
    return {
      getActionKind: () => model.get("action_kind"),
    };
  },

  render({ model, el, signal }) {
    const root = document.createElement("div");
    root.className = `anylumino-ActionHost anylumino-${model.get("action_kind")}Host`;
    root.style.width = cssSize(model.get("width"), "100%");
    root.style.height = cssSize(model.get("height"), "auto");
    const theme = document.createElement("sp-theme");
    theme.className = "anylumino-ActionTheme";
    theme.color = "light";
    theme.scale = "medium";
    theme.append(root);
    el.replaceChildren(theme);

    let panel = null;
    let iconObserver = null;

    const activate = (id) => {
      model.send({ type: "activate", id });
    };

    const clearPanel = () => {
      if (panel) {
        panel.dispose();
      }
      iconObserver?.disconnect();
      iconObserver = null;
      panel = null;
      root.replaceChildren();
    };

    const renderPanel = () => {
      clearPanel();
      const kind = model.get("action_kind");
      if (kind === "menubar") {
        panel = createMenuBar(model, activate);
      } else if (kind === "command_palette") {
        panel = createCommandPalette(model, activate);
      } else {
        panel = createToolbar(model, activate);
      }
      Widget.attach(panel, root);
      iconObserver = decorateCommandIcons(model.get("actions") ?? []);
    };

    const syncSize = () => {
      root.style.width = cssSize(model.get("width"), "100%");
      root.style.height = cssSize(model.get("height"), "auto");
      panel?.update();
    };

    model.on("change:actions", renderPanel);
    model.on("change:action_kind", renderPanel);
    model.on("change:width", syncSize);
    model.on("change:height", syncSize);

    signal.addEventListener(
      "abort",
      () => {
        clearPanel();
        removeModelListener(model, "change:actions", renderPanel);
        removeModelListener(model, "change:action_kind", renderPanel);
        removeModelListener(model, "change:width", syncSize);
        removeModelListener(model, "change:height", syncSize);
        theme.remove();
      },
      { once: true },
    );

    renderPanel();
  },
};
