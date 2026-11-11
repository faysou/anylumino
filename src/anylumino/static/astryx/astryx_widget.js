import React from "react";
import { flushSync } from "react-dom";
import { createRoot } from "react-dom/client";
import "@astryxdesign/core/reset.css";
import "@astryxdesign/core/astryx.css";
import "@astryxdesign/theme-butter/theme.css";
import "@astryxdesign/theme-chocolate/theme.css";
import "@astryxdesign/theme-gothic/theme.css";
import "@astryxdesign/theme-matcha/theme.css";
import "@astryxdesign/theme-neutral/theme.css";
import "@astryxdesign/theme-stone/theme.css";
import "@astryxdesign/theme-y2k/theme.css";
import { FormLayout } from "@astryxdesign/core/FormLayout";
import { Theme, defineTheme, generateThemeCSS } from "@astryxdesign/core/theme";
import { butterTheme } from "@astryxdesign/theme-butter/built";
import { chocolateTheme } from "@astryxdesign/theme-chocolate/built";
import { gothicTheme } from "@astryxdesign/theme-gothic/built";
import { matchaTheme } from "@astryxdesign/theme-matcha/built";
import { neutralTheme } from "@astryxdesign/theme-neutral/built";
import { stoneTheme } from "@astryxdesign/theme-stone/built";
import { y2kTheme } from "@astryxdesign/theme-y2k/built";
import "@astryxdesign/richtext/richtext.css";
import { combineSignals, cssSize, removeModelListener, renderWidgetRef } from "../layout/composition.js";
import {
  childSignature,
  modelProps,
  observeJupyterLabTheme,
  registeredComponent,
  resolveColorMode,
} from "./astryx_bridge.mjs";
import { claimDocumentTheme, claimThemeCSS } from "./astryx_theme.mjs";
import { SPECS as CHAT_SPECS } from "./components/chat.mjs";
import { SPECS as DATA_SPECS } from "./components/data.mjs";
import { SPECS as INPUT_SPECS } from "./components/inputs.mjs";
import { SPECS as LAYOUT_SPECS } from "./components/layout.mjs";
import { componentName, continuousUpdate, rawProps, setModelValue, textFor, traitProps } from "./components/model.mjs";
import { ownSlots, slotsOrText } from "./components/slots.mjs";
import { SPECS as SURFACE_SPECS } from "./components/surfaces.mjs";
import "./astryx_widget.css";

/**
 * How each Astryx component renders, by component name. A spec gives the React
 * `component` to render (or `pick`, which chooses one from the props), or a
 * `view` that renders the whole widget from the model. `props` maps the
 * component context to React props, `children` returns the React children,
 * `reserved` lists synced props the component must not receive, `traits` lists
 * the shared traits it receives as same-named props (see `traitProps`), and
 * `labelRow` lets `labelPosition="left"` place the label beside the control.
 */
const SPECS = { ...CHAT_SPECS, ...DATA_SPECS, ...INPUT_SPECS, ...LAYOUT_SPECS, ...SURFACE_SPECS };

// The built themes bundled with anylumino, by name. Their CSS is in the widget
// stylesheet, so a descriptor that names one needs no CSS of its own.
const BUNDLED_THEMES = Object.fromEntries(
  [butterTheme, chocolateTheme, gothicTheme, matchaTheme, neutralTheme, stoneTheme, y2kTheme].map((theme) => [
    theme.name,
    theme,
  ]),
);

function brandTheme(brand) {
  if (brand.built || brand.__built) {
    const bundled = BUNDLED_THEMES[String(brand.name ?? "neutral")];
    if (bundled && !brand.css) {
      return bundled;
    }
    return {
      name: String(brand.name ?? "neutral"),
      __built: true,
      tokens: brand.tokens ?? {},
      components: brand.components ?? undefined,
    };
  }
  const tokens = brand.tokens ?? brand;
  if (!tokens || Object.keys(tokens).length === 0) {
    return neutralTheme;
  }
  const normalizedTokens = {};
  for (const [name, value] of Object.entries(tokens)) {
    const tokenName = String(name).startsWith("--") ? String(name) : `--${name}`;
    normalizedTokens[tokenName] = value;
  }
  // Runtime brands are marked built so Astryx skips its own injection: it
  // dedupes by theme name and drops the shared style tag when the first
  // injecting widget unmounts, stripping tokens from the widgets that remain.
  return { ...defineTheme({ name: String(brand.name ?? "anylumino-brand"), tokens: normalizedTokens }), __built: true };
}

function themeCSS(brand, theme) {
  if (brand.built || brand.__built) {
    return typeof brand.css === "string" ? brand.css : "";
  }
  if (theme === neutralTheme) {
    return "";
  }
  const { prose, component } = generateThemeCSS(theme);
  return [prose && `@layer reset {\n${prose}\n}`, component && `@layer astryx-theme {\n${component}\n}`]
    .filter(Boolean)
    .join("\n\n");
}

function useThemeCSS(themeName, css, styleRoot) {
  React.useInsertionEffect(() => claimThemeCSS(themeName, css, styleRoot), [themeName, css, styleRoot]);
}

function useDocumentThemeGuard() {
  React.useInsertionEffect(() => claimDocumentTheme(), []);
}

function useColorMode(mode) {
  const [resolved, setResolved] = React.useState(() => resolveColorMode(mode));
  React.useEffect(() => {
    setResolved(resolveColorMode(mode));
    if (mode !== "jupyterlab") {
      return undefined;
    }
    return observeJupyterLabTheme(setResolved);
  }, [mode]);
  return resolved;
}

/**
 * Uncommitted editing state for controls whose model updates are deferred by
 * `continuous_update=False`. The draft keeps the control responsive while
 * Python only sees the value once the edit ends.
 */
function useDraft() {
  const [draft, setDraft] = React.useState(null);
  const pending = React.useRef(null);
  pending.current = draft;
  return {
    has: draft !== null,
    value: draft?.value,
    set: (next) => {
      pending.current = { value: next };
      setDraft(pending.current);
    },
    clear: () => {
      pending.current = null;
      setDraft(null);
    },
    commit: (model) => {
      const edit = pending.current;
      pending.current = null;
      setDraft(null);
      if (edit !== null) {
        setModelValue(model, edit.value);
      }
    },
  };
}

/**
 * Distinct id per React root, counted on the global so it stays unique when the
 * host loads this module more than once, which JupyterLab does per widget.
 */
function nextReactRootId() {
  globalThis.__anyluminoReactRoots = (globalThis.__anyluminoReactRoots ?? 0) + 1;
  return globalThis.__anyluminoReactRoots;
}

/**
 * The values every component spec reads from the model, resolved once per render.
 */
function componentContext(model, spec, draft, elementId) {
  const props = { ...modelProps(model, spec.reserved ?? []), ...traitProps(model, spec.traits) };
  const value = model.get("value");
  const isContinuous = continuousUpdate(model);
  return {
    model,
    name: componentName(model),
    props,
    label: String(model.get("label") || props.label || textFor(model)),
    variant: String(model.get("variant") || props.variant || ""),
    value,
    disabled: Boolean(model.get("disabled")),
    draft,
    elementId,
    isContinuous,
    editedValue: isContinuous || !draft.has ? value : draft.value,
  };
}

function AstryxModelView({ model, styleRoot, mountChildren }) {
  const name = componentName(model);
  const mode = useColorMode(String(model.get("color_mode") || "light"));
  const brandKey = JSON.stringify(model.get("brand") ?? {});
  const theme = React.useMemo(() => brandTheme(model.get("brand") ?? {}), [brandKey]);
  const css = React.useMemo(() => themeCSS(model.get("brand") ?? {}, theme), [brandKey, theme]);
  useThemeCSS(theme.name, css, styleRoot);
  useDocumentThemeGuard();
  const draft = useDraft();
  const elementId = React.useId();
  let spec;
  try {
    spec = registeredComponent(SPECS, name);
  } catch (error) {
    // A name this bundle does not know, such as one from a newer anylumino, shows
    // in the output instead of failing the whole widget.
    return React.createElement("div", { className: "anylumino-UnknownComponent", role: "alert" }, error.message);
  }
  const ctx = componentContext(model, spec, draft, elementId);
  const props = spec.props ? spec.props(ctx) : ctx.props;
  const component = spec.view
    ? React.createElement(spec.view, { model, props, mountChildren })
    : React.createElement(spec.pick ? spec.pick(props) : spec.component, props, (spec.children ?? slotsOrText)(ctx));
  const horizontalLabel = Boolean(spec.labelRow) && rawProps(model).labelPosition === "left" && !props.isLabelHidden;

  return React.createElement(
    Theme,
    { theme, mode },
    React.createElement(
      "div",
      {
        className: `anylumino-AstryxWidgetHost anylumino-${name}Host`,
        style: {
          width: cssSize(model.get("width"), ""),
          height: cssSize(model.get("height"), ""),
        },
      },
      horizontalLabel
        ? React.createElement(FormLayout, {
          direction: "horizontal-labels",
          className: "anylumino-InputLabelRow",
          style: {
            "--anylumino-input-label-width": cssSize(rawProps(model).labelWidth, "auto"),
            alignItems: props.description || props.status?.message ? undefined : "center",
          },
        }, component)
        : component,
    ),
  );
}

/**
 * Render each composed child once, into a host element of its own, and put
 * that host into the slot React laid out for the child.
 *
 * React removes a slot whose component hides its content, such as a closed
 * dialog, and makes a new one when the content shows again. The host outlives
 * the slot, so the child keeps its state and stays one view instead of being
 * rendered again. Hosts last until the composed children change, which aborts
 * `childSignal` and starts a new `childHosts` map.
 */
async function renderChildren(model, host, rootElement, childSignal, childHosts) {
  const refs = model.get("widgets") ?? [];
  if (refs.length === 0) {
    return;
  }
  await Promise.resolve();
  // Resolved before the first child mounts, because a mounted child contributes
  // slots of its own and a later lookup would find those instead of ours.
  const slots = ownSlots(model, rootElement);
  for (const [index, ref] of refs.entries()) {
    const slot = slots.get(String(index));
    if (!slot || childSignal.aborted) {
      continue;
    }
    const childHost = childHosts.get(index);
    if (childHost !== undefined) {
      if (childHost.parentElement !== slot) {
        slot.replaceChildren(childHost);
      }
      continue;
    }
    // Claimed before the child renders, since a panel view can request a mount
    // while a model change already runs one.
    const created = document.createElement("div");
    created.className = "anylumino-AstryxChildHost";
    childHosts.set(index, created);
    slot.replaceChildren(created);
    await renderWidgetRef(model, host, ref, created, childSignal);
  }
}

export default {
  async render({ model, el, signal, host }) {
    if (!host?.getWidget && (model.get("widgets") ?? []).length > 0) {
      throw new Error("[anylumino] The current anywidget host does not support widget composition.");
    }

    // Astryx names CSS anchors from React useId values. Every widget is its own
    // React root, and roots restart useId from the same counter, so without a
    // distinct prefix per root the anchor names collide and a popover positions
    // against another widget's trigger.
    const reactRoot = createRoot(el, { identifierPrefix: `al${nextReactRootId()}-` });
    const styleRoot = el.getRootNode();
    let childController = new AbortController();
    let childKey = childSignature(model);
    let childHosts = new Map();
    let scheduled = false;

    // Panel views create slots from their own state, such as a measured pane
    // size, and ask for the children to be mounted once those slots exist.
    const mountChildren = () => {
      void renderChildren(model, host, el, combineSignals(signal, childController.signal), childHosts);
    };

    const renderCurrent = () => {
      const nextChildKey = childSignature(model);
      if (nextChildKey !== childKey) {
        childController.abort();
        childController = new AbortController();
        childKey = nextChildKey;
        childHosts = new Map();
      }
      flushSync(() => {
        reactRoot.render(React.createElement(AstryxModelView, { model, styleRoot, mountChildren }));
      });
      mountChildren();
    };

    // A single Python mutation lands as several trait changes, so renders are
    // coalesced into one pass instead of one flushSync per trait.
    const scheduleRender = () => {
      if (scheduled) {
        return;
      }
      scheduled = true;
      queueMicrotask(() => {
        scheduled = false;
        if (!signal.aborted) {
          renderCurrent();
        }
      });
    };

    const watched = [
      "component_name",
      "component_kind",
      "widgets",
      "child_keys",
      "titles",
      "selected_index",
      "sizes",
      "text",
      "label",
      "value",
      "is_open",
      "disabled",
      "variant",
      "width",
      "height",
      "selected",
      "selects",
      "sort_key",
      "sort_direction",
      "sortable",
      "select_all_label",
      "props",
      "color_mode",
      "brand",
      "continuous_update",
      "search_mode",
      "messages",
      "is_streaming",
      "placeholder",
    ];

    watched.forEach((name) => model.on(`change:${name}`, scheduleRender));
    signal.addEventListener(
      "abort",
      () => {
        childController.abort();
        watched.forEach((name) => removeModelListener(model, `change:${name}`, scheduleRender));
        reactRoot.unmount();
      },
      { once: true },
    );
    renderCurrent();
  },
};
