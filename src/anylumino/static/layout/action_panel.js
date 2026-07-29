import {
  CommandPalette,
  Menu,
  MenuBar,
  Panel,
  Widget,
} from "@lumino/widgets";
import { CommandRegistry } from "@lumino/commands";
import { cssSize, modelListeners } from "./composition.js";

const ICON_PATHS = {
  AddContent: ["M12 5v14", "M5 12h14"],
  ArrowDown: ["m6 9 6 6 6-6"],
  ArrowUp: ["m18 15-6-6-6 6"],
  CheckmarkCircle: ["M22 11.1V12a10 10 0 1 1-5.9-9.1", "m9 11 3 3L22 4"],
  Circle: ["M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20"],
  CircleFilled: ["M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20"],
  ClockPending: ["M12 8v5l3 2", "M12 2a10 10 0 1 0 10 10"],
  Comment: ["M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4Z"],
  Date: ["M3 5h18v16H3Z", "M16 3v4", "M8 3v4", "M3 10h18"],
  FullScreen: ["M8 3H3v5", "M16 3h5v5", "M8 21H3v-5", "M16 21h5v-5"],
  GraphTrend: ["m3 17 6-6 4 4 8-9", "M17 6h4v4"],
  HelpCircle: [
    "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20",
    "M9.1 9a3 3 0 1 1 4.8 2.4c-1.2.8-1.9 1.4-1.9 2.6",
    "M12 18h.01",
  ],
  InfoCircle: ["M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20", "M12 10v6", "M12 7h.01"],
  Light: ["M12 2a7 7 0 0 0 0 14Z", "M12 2v20"],
  Magnify: ["M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16", "m21 21-4.4-4.4"],
  RotateRight: ["M21 12a9 9 0 1 1-2.6-6.4L21 8", "M21 3v5h-5"],
  Star: ["m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8-6.2-3.2L5.8 21 7 14.2 2 9.3l6.9-1Z"],
  StepForward: ["m5 4 10 8L5 20Z", "M19 5v14"],
  Upload: ["M12 16V3", "m7 8 5-5 5 5", "M5 21h14"],
};

const ICON_SIZES = {
  s: 16,
  m: 18,
  l: 20,
  xl: 24,
  xxl: 28,
};

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
  const size = ICON_SIZES[spec.size] ?? ICON_SIZES.s;
  if (spec.src) {
    const icon = document.createElement("img");
    icon.className = "anylumino-ToolbarIcon";
    icon.src = spec.src;
    icon.width = size;
    icon.height = size;
    if (spec.label) {
      icon.alt = spec.label;
    } else {
      icon.alt = "";
      icon.setAttribute("aria-hidden", "true");
    }
    return icon;
  }

  const paths = ICON_PATHS[spec.name];
  if (!paths) {
    return null;
  }

  const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  icon.setAttribute("class", "anylumino-ToolbarIcon");
  icon.setAttribute("viewBox", "0 0 24 24");
  icon.setAttribute("width", String(size));
  icon.setAttribute("height", String(size));
  icon.setAttribute("fill", spec.name === "CircleFilled" ? "currentColor" : "none");
  icon.setAttribute("stroke", "currentColor");
  icon.setAttribute("stroke-width", "2");
  icon.setAttribute("stroke-linecap", "round");
  icon.setAttribute("stroke-linejoin", "round");
  for (const pathData of paths) {
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", pathData);
    icon.append(path);
  }
  if (spec.label) {
    icon.setAttribute("role", "img");
    icon.setAttribute("aria-label", spec.label);
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
    const button = document.createElement("button");
    button.type = "button";
    button.className = "anylumino-ToolbarButton";
    button.dataset.actionId = id;
    button.dataset.size = String(action.size ?? "s");
    button.disabled = Boolean(action.disabled);
    button.title = String(action.tooltip ?? action.caption ?? actionLabel(action));
    button.classList.toggle("anylumino-mod-quiet", action.quiet ?? true);

    const icon = createIcon(action);
    if (icon) {
      button.classList.add("anylumino-ToolbarButtonIconOnly");
      button.setAttribute("aria-label", actionLabel(action));
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

    const unbind = modelListeners(model, [
      ["actions", renderPanel],
      ["action_kind", renderPanel],
      ["width", syncSize],
      ["height", syncSize],
    ]);

    signal.addEventListener(
      "abort",
      () => {
        clearPanel();
        unbind();
        root.remove();
      },
      { once: true },
    );

    renderPanel();
  },
};
