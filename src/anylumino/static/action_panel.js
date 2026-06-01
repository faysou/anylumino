import {
  CommandPalette,
  Menu,
  MenuBar,
  Panel,
  Widget,
} from "https://esm.sh/@lumino/widgets@2.8.0?bundle";
import { CommandRegistry } from "https://esm.sh/@lumino/commands@2.3.3?bundle";
import "https://esm.sh/@awesome.me/webawesome@3.7.0/dist/components/icon/icon.js?bundle";

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

function iconSpec(action) {
  const name = String(action?.icon ?? "").trim();
  if (!name) {
    return null;
  }
  return {
    name,
    family: String(action?.icon_family ?? "classic"),
    variant: String(action?.icon_variant ?? "solid"),
    library: String(action?.icon_library ?? "default"),
  };
}

function createIcon(action) {
  const spec = iconSpec(action);
  if (!spec) {
    return null;
  }
  const icon = document.createElement("wa-icon");
  icon.className = "anylumino-ToolbarIcon";
  icon.name = spec.name;
  icon.family = spec.family;
  icon.variant = spec.variant;
  icon.library = spec.library;
  icon.setAttribute("aria-hidden", "true");
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
    const button = document.createElement("button");
    button.type = "button";
    button.className = "anylumino-ToolbarButton";
    button.dataset.actionId = id;
    button.disabled = Boolean(action.disabled);
    button.title = String(action.tooltip ?? action.caption ?? actionLabel(action));
    button.setAttribute("aria-label", actionLabel(action));

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
    el.replaceChildren(root);

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
        root.remove();
      },
      { once: true },
    );

    renderPanel();
  },
};
