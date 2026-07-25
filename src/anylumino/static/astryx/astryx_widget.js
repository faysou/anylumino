import React from "react";
import { flushSync } from "react-dom";
import { createRoot } from "react-dom/client";
import "@astryxdesign/core/reset.css";
import "@astryxdesign/core/astryx.css";
import "@astryxdesign/theme-neutral/theme.css";
import { AlertDialog } from "@astryxdesign/core/AlertDialog";
import { AspectRatio } from "@astryxdesign/core/AspectRatio";
import { Avatar } from "@astryxdesign/core/Avatar";
import { AvatarGroup, AvatarGroupOverflow } from "@astryxdesign/core/AvatarGroup";
import { Badge } from "@astryxdesign/core/Badge";
import { Banner } from "@astryxdesign/core/Banner";
import { Blockquote } from "@astryxdesign/core/Blockquote";
import { Breadcrumbs, BreadcrumbItem } from "@astryxdesign/core/Breadcrumbs";
import { Button } from "@astryxdesign/core/Button";
import { ButtonGroup } from "@astryxdesign/core/ButtonGroup";
import { Calendar } from "@astryxdesign/core/Calendar";
import { Card } from "@astryxdesign/core/Card";
import { Center } from "@astryxdesign/core/Center";
import { CheckboxInput } from "@astryxdesign/core/CheckboxInput";
import { CheckboxList, CheckboxListItem } from "@astryxdesign/core/CheckboxList";
import { ClickableCard } from "@astryxdesign/core/ClickableCard";
import { Citation } from "@astryxdesign/core/Citation";
import { Code } from "@astryxdesign/core/Code";
import { CodeBlock } from "@astryxdesign/core/CodeBlock";
import { Collapsible } from "@astryxdesign/core/Collapsible";
import { CommandPalette } from "@astryxdesign/core/CommandPalette";
import { DateInput } from "@astryxdesign/core/DateInput";
import { DateRangeInput } from "@astryxdesign/core/DateRangeInput";
import { DateTimeInput } from "@astryxdesign/core/DateTimeInput";
import { Dialog } from "@astryxdesign/core/Dialog";
import { Divider } from "@astryxdesign/core/Divider";
import { DropdownMenu } from "@astryxdesign/core/DropdownMenu";
import { EmptyState } from "@astryxdesign/core/EmptyState";
import { Field } from "@astryxdesign/core/Field";
import { FieldStatus } from "@astryxdesign/core/FieldStatus";
import { FileInput } from "@astryxdesign/core/FileInput";
import { FormLayout } from "@astryxdesign/core/FormLayout";
import { Grid } from "@astryxdesign/core/Grid";
import { HoverCard } from "@astryxdesign/core/HoverCard";
import { Icon } from "@astryxdesign/core/Icon";
import { IconButton } from "@astryxdesign/core/IconButton";
import { InputGroup, InputGroupText } from "@astryxdesign/core/InputGroup";
import { Item } from "@astryxdesign/core/Item";
import { Kbd } from "@astryxdesign/core/Kbd";
import { Link } from "@astryxdesign/core/Link";
import { Lightbox } from "@astryxdesign/core/Lightbox";
import { List, ListItem } from "@astryxdesign/core/List";
import { Markdown } from "@astryxdesign/core/Markdown";
import { MetadataList, MetadataListItem } from "@astryxdesign/core/MetadataList";
import { MoreMenu } from "@astryxdesign/core/MoreMenu";
import { MultiSelector } from "@astryxdesign/core/MultiSelector";
import { NumberInput } from "@astryxdesign/core/NumberInput";
import { Outline } from "@astryxdesign/core/Outline";
import { Overlay } from "@astryxdesign/core/Overlay";
import { Pagination } from "@astryxdesign/core/Pagination";
import { Popover } from "@astryxdesign/core/Popover";
import { ProgressBar } from "@astryxdesign/core/ProgressBar";
import { RadioList, RadioListItem } from "@astryxdesign/core/RadioList";
import { Section } from "@astryxdesign/core/Section";
import { SegmentedControl, SegmentedControlItem } from "@astryxdesign/core/SegmentedControl";
import { SelectableCard } from "@astryxdesign/core/SelectableCard";
import { Selector } from "@astryxdesign/core/Selector";
import { Skeleton } from "@astryxdesign/core/Skeleton";
import { Slider } from "@astryxdesign/core/Slider";
import { Spinner } from "@astryxdesign/core/Spinner";
import { HStack, Stack, VStack } from "@astryxdesign/core/Stack";
import { StatusDot } from "@astryxdesign/core/StatusDot";
import { Switch } from "@astryxdesign/core/Switch";
import {
  Table,
  pixel,
  proportional,
  useTableSelection,
  useTableSortable,
} from "@astryxdesign/core/Table";
import { TabList, Tab } from "@astryxdesign/core/TabList";
import { Heading, Text } from "@astryxdesign/core/Text";
import { TextArea } from "@astryxdesign/core/TextArea";
import { TextInput } from "@astryxdesign/core/TextInput";
import { Thumbnail } from "@astryxdesign/core/Thumbnail";
import { TimeInput } from "@astryxdesign/core/TimeInput";
import { Timestamp } from "@astryxdesign/core/Timestamp";
import { ToggleButton, ToggleButtonGroup } from "@astryxdesign/core/ToggleButton";
import { Token } from "@astryxdesign/core/Token";
import { Tokenizer } from "@astryxdesign/core/Tokenizer";
import { Toolbar } from "@astryxdesign/core/Toolbar";
import { Tooltip } from "@astryxdesign/core/Tooltip";
import { TreeList } from "@astryxdesign/core/TreeList";
import { Typeahead, createStaticSource } from "@astryxdesign/core/Typeahead";
import { Theme, defineTheme, generateThemeCSS } from "@astryxdesign/core/theme";
import { neutralTheme } from "@astryxdesign/theme-neutral/built";
import {
  clampIndex,
  combineSignals,
  cssSize,
  removeModelListener,
  renderWidgetRef,
} from "../layout/composition.js";
import {
  childSignature,
  logExponent,
  logValue,
  modelProps,
  observeJupyterLabTheme,
  registeredComponent,
  resolveColorMode,
  sendModelAction,
  setModelOpen,
  toggleGroupValue,
} from "./astryx_bridge.mjs";
import { claimDocumentTheme, claimThemeCSS } from "./astryx_theme.mjs";
import "./astryx_widget.css";

const COMPONENTS = {
  AlertDialog,
  AspectRatio,
  Avatar,
  AvatarGroup,
  Badge,
  Banner,
  Blockquote,
  Breadcrumbs,
  Button,
  ButtonGroup,
  Calendar,
  Card,
  Center,
  CheckboxInput,
  CheckboxList,
  Citation,
  ClickableCard,
  Code,
  CodeBlock,
  Collapsible,
  CommandPalette,
  DateInput,
  DateRangeInput,
  DateTimeInput,
  Dialog,
  Divider,
  DropdownMenu,
  EmptyState,
  Field,
  FieldStatus,
  FileInput,
  FormLayout,
  Grid,
  HoverCard,
  Heading,
  Icon,
  IconButton,
  InputGroup,
  Item,
  Kbd,
  Link,
  Lightbox,
  List,
  Markdown,
  MetadataList,
  MoreMenu,
  MultiSelector,
  NumberInput,
  Outline,
  Overlay,
  Pagination,
  Popover,
  ProgressBar,
  RadioList,
  Section,
  SegmentedControl,
  SelectableCard,
  Selector,
  Skeleton,
  Slider,
  Spinner,
  Stack,
  StatusDot,
  Switch,
  Table,
  TabList,
  Text,
  TextArea,
  TextInput,
  Thumbnail,
  TimeInput,
  Timestamp,
  ToggleButton,
  ToggleButtonGroup,
  Token,
  Tokenizer,
  Toolbar,
  Tooltip,
  TreeList,
  Typeahead,
};

const PROP_DRIVEN_COMPONENTS = new Set([
  "AlertDialog",
  "Avatar",
  "Badge",
  "Button",
  "Calendar",
  "CheckboxInput",
  "Citation",
  "CodeBlock",
  "CommandPalette",
  "DateInput",
  "DateRangeInput",
  "DateTimeInput",
  "Dialog",
  "Divider",
  "DropdownMenu",
  "EmptyState",
  "FieldStatus",
  "FileInput",
  "Icon",
  "IconButton",
  "Lightbox",
  "Kbd",
  "MultiSelector",
  "MoreMenu",
  "NumberInput",
  "Outline",
  "Pagination",
  "ProgressBar",
  "SelectableCard",
  "Selector",
  "LogSlider",
  "SelectionSlider",
  "Skeleton",
  "Slider",
  "Spinner",
  "StatusDot",
  "Switch",
  "Table",
  "TextArea",
  "TextInput",
  "Thumbnail",
  "TimeInput",
  "Timestamp",
  "ToggleButton",
  "Token",
  "Tokenizer",
  "TreeList",
  "Typeahead",
]);

const GENERATED_CHILD_COMPONENTS = new Set([
  "Breadcrumbs",
  "AvatarGroup",
  "ButtonGroup",
  "CheckboxList",
  "List",
  "MetadataList",
  "RadioList",
  "SegmentedControl",
  "TabList",
  "ToggleButtonGroup",
]);

function textFor(model) {
  return String(model.get("text") || model.get("label") || model.get("value") || "");
}

function setModelValue(model, value) {
  model.set("value", value);
  model.save_changes();
}

function continuousUpdate(model) {
  return model.get("continuous_update") !== false;
}

function setBooleanValue(model, value) {
  setModelValue(model, Boolean(value));
}

function setStringValue(model, value) {
  setModelValue(model, value == null ? "" : String(value));
}

function setNullableStringValue(model, value) {
  setModelValue(model, value == null ? null : String(value));
}

function setNumberValue(model, value) {
  setModelValue(model, value == null || value === "" ? null : Number(value));
}

function setArrayValue(model, value) {
  setModelValue(model, Array.isArray(value) ? value : []);
}

function setItemValue(model, item) {
  setModelValue(model, item == null ? null : String(item.id ?? item.value ?? item.label ?? ""));
}

function setItemArrayValue(model, items) {
  setArrayValue(model, asArray(items).map((item) => String(item.id ?? item.value ?? item.label ?? "")));
}

function fileInputValue(files, isMultiple) {
  if (!files) {
    return isMultiple ? [] : null;
  }
  const fileList = Array.isArray(files) ? files : [files];
  const records = fileList.map((file) => ({
    name: file.name,
    size: file.size,
    type: file.type,
    lastModified: file.lastModified,
  }));
  return isMultiple ? records : (records[0] ?? null);
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function rawProps(model) {
  return { ...(model.get("props") ?? {}) };
}

function brandTheme(brand) {
  if (brand.built || brand.__built) {
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

function useThemeCSS(themeName, css) {
  React.useInsertionEffect(() => claimThemeCSS(themeName, css), [themeName, css]);
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

function searchableItems(items) {
  return asArray(items).map((item, index) => {
    if (item && typeof item === "object") {
      const id = String(item.id ?? item.value ?? item.label ?? index);
      return {
        ...item,
        id,
        label: itemLabel(item, `Item ${index + 1}`),
      };
    }
    return {
      id: String(item ?? index),
      label: String(item ?? `Item ${index + 1}`),
    };
  });
}

let searchRequestCounter = 0;

/**
 * Distinct id per React root, counted on the global so it stays unique when the
 * host loads this module more than once, which JupyterLab does per widget.
 */
function nextReactRootId() {
  globalThis.__anyluminoReactRoots = (globalThis.__anyluminoReactRoots ?? 0) + 1;
  return globalThis.__anyluminoReactRoots;
}

function requestPythonSearch(model, query) {
  const requestId = `${model.model_id ?? "model"}-${Date.now()}-${++searchRequestCounter}`;
  return new Promise((resolve) => {
    let settled = false;
    const finish = (items) => {
      if (settled) {
        return;
      }
      settled = true;
      clearTimeout(timeout);
      removeModelListener(model, "msg:custom", onMessage);
      resolve(searchableItems(items));
    };
    const onMessage = (content) => {
      if (content?.type !== "search-results" || String(content.request_id ?? "") !== requestId) {
        return;
      }
      finish(content.items ?? []);
    };
    const timeout = setTimeout(() => finish([]), 10000);
    model.on("msg:custom", onMessage);
    model.send({ type: "search", request_id: requestId, query: String(query ?? "") });
  });
}

function searchSourceFor(model, items) {
  if (String(model.get("search_mode") || "static") !== "python") {
    return createStaticSource(items);
  }
  return {
    search: (query) => requestPythonSearch(model, query),
    bootstrap: () => requestPythonSearch(model, ""),
  };
}

function selectedSearchItem(items, value) {
  if (value == null || value === "") {
    return null;
  }
  const selectedId = String(value);
  return items.find((item) => String(item.id) === selectedId) ?? null;
}

function selectedSearchItems(items, value) {
  const selectedIds = new Set(asArray(value).map(String));
  return items.filter((item) => selectedIds.has(String(item.id)));
}

function iconNode(icon, props = {}) {
  if (!icon) {
    return undefined;
  }
  if (typeof icon === "string") {
    return React.createElement(Icon, { icon, ...props });
  }
  return icon;
}

function tableWidth(width) {
  if (typeof width === "number") {
    return proportional(width);
  }
  if (width && typeof width === "object") {
    if (width.kind === "pixel") {
      return pixel(Number(width.value));
    }
    if (width.kind === "proportional") {
      return proportional(Number(width.value ?? 1));
    }
  }
  return width;
}

function tableColumns(columns, sortable = false) {
  return asArray(columns).map((column) => ({
    ...column,
    width: tableWidth(column.width),
    sortable: column.sortable ?? (sortable ? true : undefined),
  }));
}

function tableRowId(row, idKey, index = 0) {
  return String(row?.[idKey] ?? index);
}

function tableSortDirectionForAstryx(direction) {
  if (direction === "asc" || direction === "ascending") {
    return "ascending";
  }
  if (direction === "desc" || direction === "descending") {
    return "descending";
  }
  return "";
}

function tableSortDirectionForModel(direction) {
  if (direction === "ascending") {
    return "asc";
  }
  if (direction === "descending") {
    return "desc";
  }
  return "";
}

function compareTableValues(direction, leftValue, rightValue) {
  if (leftValue == null && rightValue == null) {
    return 0;
  }
  if (leftValue == null) {
    return 1;
  }
  if (rightValue == null) {
    return -1;
  }
  let result = 0;
  if (typeof leftValue === "number" && typeof rightValue === "number") {
    result = leftValue - rightValue;
  } else {
    result = String(leftValue).localeCompare(String(rightValue), undefined, {
      numeric: true,
      sensitivity: "base",
    });
  }
  return direction === "descending" ? -result : result;
}

function sortedTableData(data, sort) {
  if (!sort.length) {
    return data;
  }
  return [...data].sort((left, right) => {
    for (const entry of sort) {
      const result = compareTableValues(entry.direction, left?.[entry.sortKey], right?.[entry.sortKey]);
      if (result !== 0) {
        return result;
      }
    }
    return 0;
  });
}

function setTableSelection(model, selected) {
  const nextSelected = selected.map(String);
  model.set("selected", nextSelected);
  model.save_changes();
  model.send({ type: "selection", selected: nextSelected });
}

function setTableSort(model, sort) {
  const primarySort = sort[0] ?? {};
  const sortKey = String(primarySort.sortKey ?? "");
  const sortDirection = tableSortDirectionForModel(primarySort.direction);
  model.set("sort_key", sortKey);
  model.set("sort_direction", sortDirection);
  model.save_changes();
  model.send({ type: "sort", sort_key: sortKey, sort_direction: sortDirection });
}

function slotChildren(model) {
  const refs = model.get("widgets") ?? [];
  if (refs.length === 0) {
    return null;
  }
  const keys = model.get("child_keys") ?? [];
  return refs.map((_ref, index) => slotChild(model, keys[index] ?? "", index));
}

function slotChild(model, key, index) {
  return React.createElement("div", {
    className: "anylumino-AstryxChild",
    "data-anylumino-key": key ?? "",
    "data-anylumino-index": String(index),
    key: `${key ?? "widget"}-${index}`,
  });
}

/**
 * Whether a slot belongs to the widget rooted at `rootElement` rather than to
 * one of its mounted children. Children mount inside a slot, so every slot they
 * contribute has one of ours between it and the root.
 */
function isOwnSlot(slot, rootElement) {
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
function ownSlots(model, rootElement) {
  const slots = new Map();
  for (const slot of rootElement.querySelectorAll(".anylumino-AstryxChild")) {
    const index = slot.dataset.anyluminoIndex;
    if (index !== undefined && !slots.has(index) && isOwnSlot(slot, rootElement)) {
      slots.set(index, slot);
    }
  }
  return slots;
}

function keyedSlotChildren(model) {
  const refs = model.get("widgets") ?? [];
  if (refs.length === 0) {
    return [];
  }
  const keys = model.get("child_keys") ?? [];
  return refs.map((_ref, index) => slotChild(model, keys[index] ?? "", index));
}

function slotByKey(model, key) {
  const refs = model.get("widgets") ?? [];
  const keys = model.get("child_keys") ?? [];
  const index = keys.indexOf(key);
  if (index < 0 || index >= refs.length) {
    return undefined;
  }
  return slotChild(model, key, index);
}

/**
 * Wire a deferred-update control: the draft drives the visible value and the
 * model only learns about it when the edit ends.
 */
function draftHandlers(model, draft, { commitOnEnter = false } = {}) {
  return {
    onChange: (nextValue) => draft.set(nextValue),
    onBlur: () => draft.commit(model),
    ...(commitOnEnter ? { onEnter: () => draft.commit(model) } : {}),
  };
}

function componentProps(model, draft, elementId) {
  const name = String(model.get("component_name") || model.get("component_kind") || "Stack");
  const reserved = GENERATED_CHILD_COMPONENTS.has(name)
    ? ["items", "tabs", "segments", "metadata"]
    : ["Typeahead", "Tokenizer", "CommandPalette"].includes(name)
      ? ["items"]
      : name === "SelectionSlider"
        ? ["options", "marks"]
        : name === "LogSlider"
          ? ["base", "minExponent", "maxExponent"]
          : [];
  const props = modelProps(model, reserved);
  const label = String(model.get("label") || props.label || textFor(model));
  const variant = String(model.get("variant") || props.variant || "");
  const value = model.get("value");
  const disabled = Boolean(model.get("disabled"));

  if (name === "Button") {
    return {
      ...props,
      label: label || "Button",
      variant: variant || "secondary",
      isDisabled: disabled,
      onClick: () => model.send({ type: "click" }),
    };
  }

  if (name === "ClickableCard") {
    return {
      ...props,
      label: label || "Card",
      variant: variant || props.variant || "default",
      isDisabled: disabled,
      onClick: () => model.send({ type: "click" }),
    };
  }

  if (name === "IconButton") {
    return {
      ...props,
      label: label || "Button",
      icon: iconNode(props.icon || model.get("icon") || "close"),
      variant: variant || props.variant || "secondary",
      isDisabled: disabled,
      onClick: () => model.send({ type: "click" }),
    };
  }

  if (name === "ToggleButton") {
    return {
      ...props,
      label: label || "Toggle",
      isPressed: Boolean(value),
      isDisabled: disabled,
      onPressedChange: (nextValue) => setBooleanValue(model, nextValue),
    };
  }

  if (name === "ToggleButtonGroup") {
    const isMultiple = props.type === "multiple";
    return {
      ...props,
      label: label || "Toggle buttons",
      type: isMultiple ? "multiple" : "single",
      value: toggleGroupValue(value, isMultiple),
      isDisabled: disabled,
      onChange: (nextValue) => setModelValue(model, nextValue),
    };
  }

  const isContinuous = continuousUpdate(model);
  const editedValue = isContinuous || !draft.has ? value : draft.value;

  if (name === "TextInput") {
    return {
      ...props,
      label: label || "Text input",
      value: String(editedValue ?? ""),
      isDisabled: disabled,
      onChange: (nextValue) => setStringValue(model, nextValue),
      ...(isContinuous ? {} : draftHandlers(model, draft, { commitOnEnter: true })),
    };
  }

  if (name === "TextArea") {
    return {
      ...props,
      label: label || "Text area",
      value: String(editedValue ?? ""),
      isDisabled: disabled,
      onChange: (nextValue) => setStringValue(model, nextValue),
      ...(isContinuous ? {} : draftHandlers(model, draft)),
    };
  }

  if (name === "NumberInput") {
    return {
      ...props,
      label: label || "Number",
      value: editedValue == null || editedValue === "" ? null : Number(editedValue),
      isDisabled: disabled,
      onChange: (nextValue) => setNumberValue(model, nextValue),
      ...(isContinuous ? {} : draftHandlers(model, draft, { commitOnEnter: true })),
    };
  }

  if (name === "Slider") {
    return {
      ...props,
      label: label || "Slider",
      value: Array.isArray(editedValue) ? editedValue : Number(editedValue ?? props.min ?? 0),
      isDisabled: disabled,
      onChange: (nextValue) => (isContinuous ? setModelValue(model, nextValue) : draft.set(nextValue)),
      onChangeEnd: (nextValue) => {
        draft.clear();
        setModelValue(model, nextValue);
      },
    };
  }

  // Astryx `Slider` only steps linearly, so a logarithmic control drives it in
  // exponent space and reports `base ** exponent`.
  if (name === "LogSlider") {
    const raw = rawProps(model);
    const base = Number(raw.base ?? 10);
    const minExponent = Number(raw.minExponent ?? 0);
    const maxExponent = Number(raw.maxExponent ?? 4);
    const commit = (exponent) => setModelValue(model, logValue(exponent, base));
    return {
      ...props,
      label: label || "Slider",
      min: minExponent,
      max: maxExponent,
      value: logExponent(editedValue, base, minExponent, maxExponent),
      isDisabled: disabled,
      formatValue: (exponent) => String(Number(logValue(exponent, base).toPrecision(6))),
      onChange: (exponent) => (isContinuous ? commit(exponent) : draft.set(logValue(exponent, base))),
      onChangeEnd: (exponent) => {
        draft.clear();
        commit(exponent);
      },
    };
  }

  // Discrete option sliders drive the same linear slider over option indices and
  // report the option value, single or range depending on the value shape.
  if (name === "SelectionSlider") {
    const raw = rawProps(model);
    const options = asArray(raw.options);
    const labels = options.map((item, index) => itemLabel(item, `Option ${index + 1}`));
    const values = options.map((item, index) => itemValue(item, index));
    // The draft holds option values, matching the trait, so a deferred drag reads
    // back in the same units the slider reports.
    const selected = (index) => values[clampIndex(index, values.length)];
    const asOptions = (next) => (Array.isArray(next) ? next.map(selected) : selected(next));
    const indexOf = (candidate) => Math.max(0, values.indexOf(String(candidate)));
    const isRange = Array.isArray(editedValue);
    const commit = (next) =>
      Array.isArray(next) ? setArrayValue(model, asOptions(next)) : setModelValue(model, asOptions(next));
    return {
      ...props,
      label: label || "Slider",
      min: 0,
      max: Math.max(0, values.length - 1),
      step: 1,
      marks: raw.marks ? labels.map((text, index) => ({ value: index, label: text })) : undefined,
      value: isRange
        ? [indexOf(editedValue[0]), indexOf(editedValue[1] ?? editedValue[0])]
        : indexOf(editedValue),
      isDisabled: disabled || values.length === 0,
      formatValue: (index) => labels[clampIndex(index, labels.length)] ?? "",
      onChange: (next) => (isContinuous ? commit(next) : draft.set(asOptions(next))),
      onChangeEnd: (next) => {
        draft.clear();
        commit(next);
      },
    };
  }

  if (name === "CheckboxInput") {
    return {
      ...props,
      label: label || "Checkbox",
      value: value === "indeterminate" ? "indeterminate" : Boolean(value),
      isDisabled: disabled,
      onChange: (nextValue) => setModelValue(model, Boolean(nextValue)),
    };
  }

  if (name === "CheckboxList") {
    return {
      ...props,
      label: label || "Options",
      value: asArray(value),
      isDisabled: disabled,
      onChange: (nextValue) => setArrayValue(model, nextValue),
    };
  }

  if (name === "RadioList") {
    return {
      ...props,
      label: label || "Options",
      value: String(value ?? ""),
      isDisabled: disabled,
      onChange: (nextValue) => setStringValue(model, nextValue),
    };
  }

  if (name === "Switch") {
    return {
      ...props,
      label: label || "Switch",
      value: Boolean(value),
      isDisabled: disabled,
      onChange: (nextValue) => setModelValue(model, Boolean(nextValue)),
    };
  }

  if (["DateInput", "DateTimeInput", "TimeInput"].includes(name)) {
    return {
      ...props,
      label: label || name,
      value: value == null || value === "" ? undefined : String(value),
      isDisabled: disabled,
      onChange: (nextValue) => setNullableStringValue(model, nextValue),
    };
  }

  if (name === "Calendar") {
    return {
      ...props,
      value: value == null || value === "" ? undefined : value,
      onChange: (nextValue) => setModelValue(model, nextValue),
    };
  }

  if (name === "Timestamp") {
    return {
      ...props,
      value: value ?? props.value ?? textFor(model),
    };
  }

  if (name === "DateRangeInput") {
    return {
      ...props,
      label: label || "Date range",
      value: value ?? null,
      isDisabled: disabled,
      onChange: (nextValue) => setModelValue(model, nextValue),
    };
  }

  if (name === "Selector") {
    return {
      ...props,
      label: label || "Selector",
      value: value == null ? (props.hasClear ? null : undefined) : String(value),
      isDisabled: disabled,
      onChange: (nextValue) => setModelValue(model, nextValue),
    };
  }

  if (name === "MultiSelector") {
    return {
      ...props,
      label: label || "Multi selector",
      value: asArray(value),
      isDisabled: disabled,
      onChange: (nextValue) => setArrayValue(model, nextValue),
    };
  }

  if (name === "FileInput") {
    const isMultiple = Boolean(props.isMultiple || props.multiple);
    return {
      ...props,
      label: label || props.label || "File",
      value: null,
      isDisabled: disabled,
      isMultiple,
      onChange: (files) => setModelValue(model, fileInputValue(files, isMultiple)),
    };
  }

  if (name === "Typeahead") {
    const items = searchableItems(rawProps(model).items);
    return {
      ...props,
      label: label || props.label || "Typeahead",
      value: selectedSearchItem(items, value),
      searchSource: searchSourceFor(model, items),
      isDisabled: disabled,
      onChange: (item) => setItemValue(model, item),
      onOpenChange: (isOpen) => setModelOpen(model, isOpen),
    };
  }

  if (name === "Tokenizer") {
    const items = searchableItems(rawProps(model).items);
    return {
      ...props,
      label: label || props.label || "Tokenizer",
      value: selectedSearchItems(items, value),
      searchSource: searchSourceFor(model, items),
      isDisabled: disabled,
      onChange: (nextItems) => setItemArrayValue(model, nextItems),
    };
  }

  if (name === "CommandPalette") {
    const items = searchableItems(rawProps(model).items);
    return {
      ...props,
      label: label || props.label || "Command palette",
      isInline: props.isInline ?? true,
      isOpen: Boolean(model.get("is_open")),
      value: value == null ? undefined : String(value),
      searchSource: searchSourceFor(model, items),
      onValueChange: (nextValue) => setStringValue(model, nextValue),
      onOpenChange: (isOpen) => setModelOpen(model, isOpen),
    };
  }

  if (name === "TabList") {
    return {
      ...props,
      value: String(value ?? ""),
      onChange: (nextValue) => setStringValue(model, nextValue),
    };
  }

  if (name === "SegmentedControl") {
    return {
      ...props,
      label: label || "Segmented control",
      value: String(value ?? ""),
      isDisabled: disabled,
      onChange: (nextValue) => setStringValue(model, nextValue),
    };
  }

  if (name === "SelectableCard") {
    return {
      ...props,
      label: label || "Selectable card",
      isSelected: Boolean(value),
      isDisabled: disabled,
      variant: variant || props.variant || "default",
      onChange: (nextValue) => setBooleanValue(model, nextValue),
    };
  }

  if (name === "Badge") {
    return {
      ...props,
      label: label || textFor(model),
      variant: variant || props.variant || "neutral",
    };
  }

  if (name === "Token") {
    return {
      ...props,
      label: label || textFor(model),
      onRemove: props.onRemove ? () => sendModelAction(model, undefined, "remove") : undefined,
      onClick: props.clickable ? () => sendModelAction(model, undefined, "click") : undefined,
    };
  }

  if (name === "Thumbnail") {
    return {
      ...props,
      isDisabled: disabled,
      onRemove: props.onRemove
        ? () => sendModelAction(model, undefined, "remove")
        : undefined,
      onClick: props.clickable
        ? () => sendModelAction(model, undefined, "click")
        : undefined,
    };
  }

  if (name === "StatusDot") {
    return {
      ...props,
      label: label || textFor(model) || "Status",
      variant: variant || props.variant || "neutral",
    };
  }

  if (name === "ProgressBar") {
    return {
      ...props,
      label: label || textFor(model) || "Progress",
      value: value == null ? props.value : Number(value),
      variant: variant || props.variant || "accent",
      isDisabled: disabled,
    };
  }

  if (name === "Banner") {
    return {
      ...props,
      onDismiss: props.isDismissable
        ? () => sendModelAction(model, undefined, "dismiss")
        : undefined,
    };
  }

  if (name === "Pagination") {
    return {
      ...props,
      page: Number(value ?? props.page ?? 1),
      onChange: (nextValue) => setNumberValue(model, nextValue),
    };
  }

  if (name === "Icon") {
    return {
      ...props,
      icon: props.icon || model.get("icon") || textFor(model) || "circle",
    };
  }

  if (name === "Avatar") {
    return {
      ...props,
      name: label || props.name || textFor(model),
    };
  }

  if (name === "Citation") {
    return {
      ...props,
      source: props.source ?? { title: label || textFor(model) },
      number: Number(value ?? props.number ?? 1),
      variant: variant || props.variant || "number",
    };
  }

  if (name === "Field") {
    return {
      ...props,
      label: label || props.label || "Field",
      inputID: props.inputID || props.inputId || elementId,
      isDisabled: disabled || props.isDisabled,
    };
  }

  if (name === "FieldStatus") {
    return {
      ...props,
      type: variant || props.type || "success",
      message: label || props.message || textFor(model),
    };
  }

  if (name === "FormLayout") {
    return {
      direction: "vertical",
      ...props,
    };
  }

  if (name === "InputGroup") {
    return {
      ...props,
      label: label || props.label || "Input group",
      isDisabled: disabled || props.isDisabled,
    };
  }

  if (name === "Collapsible") {
    return {
      ...props,
      trigger: props.trigger || label || textFor(model) || "Details",
      isOpen: Boolean(model.get("is_open")),
      onOpenChange: (isOpen) => setModelOpen(model, isOpen),
    };
  }

  if (name === "Toolbar") {
    return {
      ...props,
      label: label || props.label || "Toolbar",
      startContent: props.startContent ?? slotByKey(model, "start"),
      centerContent: props.centerContent ?? slotByKey(model, "center"),
      endContent: props.endContent ?? slotByKey(model, "end"),
    };
  }

  if (name === "Tooltip") {
    const result = {
      ...props,
      content: props.content ?? slotByKey(model, "content") ?? label ?? textFor(model),
    };
    if (props.isOpen !== undefined) {
      result.isOpen = Boolean(model.get("is_open"));
      result.onOpenChange = (isOpen) => setModelOpen(model, isOpen);
    }
    return result;
  }

  if (name === "HoverCard") {
    const result = {
      ...props,
      content: props.content ?? slotByKey(model, "content") ?? label ?? textFor(model),
    };
    if (props.isOpen !== undefined) {
      result.isOpen = Boolean(model.get("is_open"));
      result.onOpenChange = (isOpen) => setModelOpen(model, isOpen);
    }
    return result;
  }

  if (name === "Popover") {
    const result = {
      ...props,
      label: label || props.label || "Popover",
      content: props.content ?? slotByKey(model, "content") ?? label ?? textFor(model),
    };
    if (props.isOpen !== undefined) {
      result.isOpen = Boolean(model.get("is_open"));
      result.onOpenChange = (isOpen) => setModelOpen(model, isOpen);
    }
    return result;
  }

  if (name === "Overlay") {
    const result = {
      ...props,
      content: props.content ?? slotByKey(model, "content"),
    };
    if (props.isOpen !== undefined) {
      result.isOpen = Boolean(model.get("is_open"));
    }
    return result;
  }

  if (name === "Lightbox") {
    return {
      ...props,
      isOpen: Boolean(model.get("is_open")),
      index: Number(value ?? 0),
      onOpenChange: (isOpen) => setModelOpen(model, isOpen),
      onIndexChange: (nextIndex) => setNumberValue(model, nextIndex),
    };
  }

  if (name === "Dialog") {
    return {
      ...props,
      isInline: props.isInline ?? true,
      isOpen: Boolean(model.get("is_open")),
      onOpenChange: (isOpen) => setModelOpen(model, isOpen),
    };
  }

  if (name === "AlertDialog") {
    return {
      ...props,
      title: props.title || label || "Alert",
      description: props.description || textFor(model),
      actionLabel: props.actionLabel || "Continue",
      isInline: props.isInline ?? true,
      isOpen: Boolean(model.get("is_open")),
      onOpenChange: (isOpen) => setModelOpen(model, isOpen),
      onAction: () => sendModelAction(model, undefined, "confirm"),
    };
  }

  if (name === "DropdownMenu") {
    return {
      ...props,
      items: menuItems(model, rawProps(model).items),
      isMenuOpen: Boolean(model.get("is_open")),
      button: {
        label: label || props.button?.label || "Menu",
        variant: variant || props.button?.variant || "secondary",
        isDisabled: disabled,
        ...(props.button ?? {}),
      },
      onOpenChange: (isOpen) => setModelOpen(model, isOpen),
    };
  }

  if (name === "MoreMenu") {
    return {
      ...props,
      label: label || props.label || "More options",
      isDisabled: disabled,
      isMenuOpen: Boolean(model.get("is_open")),
      items: menuItems(model, rawProps(model).items),
      onOpenChange: (isOpen) => setModelOpen(model, isOpen),
    };
  }

  if (name === "Outline") {
    const originalProps = rawProps(model);
    return {
      ...props,
      items: asArray(originalProps.items),
      activeId: value || props.activeId,
      onActiveIdChange: (nextValue) => setStringValue(model, nextValue),
    };
  }

  if (name === "TreeList") {
    const originalProps = rawProps(model);
    return {
      ...props,
      items: asArray(originalProps.items),
    };
  }

  if (name === "Table") {
    const originalProps = rawProps(model);
    return {
      ...props,
      data: asArray(originalProps.rows ?? originalProps.data),
      columns: tableColumns(originalProps.columns),
      idKey: originalProps.idKey ?? "id",
    };
  }

  if (name === "Text") {
    return props;
  }

  if (name === "Heading") {
    return {
      ...props,
      level: Number(props.level ?? 3),
    };
  }

  if (name === "Stack") {
    return {
      gap: 2,
      ...props,
      width: props.width ?? cssSize(model.get("width"), undefined),
      height: props.height ?? cssSize(model.get("height"), undefined),
    };
  }

  return props;
}

function componentFor(name, props) {
  if (name === "Stack") {
    return String(props.direction || "vertical") === "horizontal" ? HStack : VStack;
  }
  if (name === "LogSlider" || name === "SelectionSlider") {
    return Slider;
  }
  return registeredComponent(COMPONENTS, name);
}

function itemLabel(item, fallback) {
  if (item && typeof item === "object") {
    return String(item.label ?? item.value ?? fallback);
  }
  return String(item ?? fallback);
}

function itemValue(item, fallback) {
  if (item && typeof item === "object") {
    return String(item.value ?? item.label ?? fallback);
  }
  return String(item ?? fallback);
}

function menuItems(model, items) {
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

function generatedChildren(model, name) {
  const props = rawProps(model);
  if (!GENERATED_CHILD_COMPONENTS.has(name)) {
    return null;
  }

  if (name === "List") {
    return asArray(props.items).map((item, index) =>
      React.createElement(ListItem, {
        key: itemValue(item, index),
        label: itemLabel(item, `Item ${index + 1}`),
        description: item && typeof item === "object" ? item.description : undefined,
        isSelected: Boolean(item?.selected),
        isDisabled: Boolean(item?.disabled),
      }),
    );
  }

  if (name === "AvatarGroup") {
    const items = asArray(props.items);
    const overflowCount = Number(props.overflowCount ?? props.overflow_count ?? 0);
    const children = items.map((item, index) =>
      React.createElement(Avatar, {
        key: itemValue(item, index),
        name: itemLabel(item, `User ${index + 1}`),
        src: item?.src,
        alt: item?.alt,
        status: item?.status,
      }),
    );
    if (overflowCount > 0) {
      children.push(React.createElement(AvatarGroupOverflow, { key: "__overflow", count: overflowCount }));
    }
    return children;
  }

  if (name === "MetadataList") {
    return asArray(props.items ?? props.metadata).map((item, index) =>
      React.createElement(
        MetadataListItem,
        {
          key: itemValue(item, index),
          label: itemLabel({ label: item?.label }, `Field ${index + 1}`),
        },
        String(item?.value ?? ""),
      ),
    );
  }

  if (name === "Breadcrumbs") {
    return asArray(props.items).map((item, index) =>
      React.createElement(
        BreadcrumbItem,
        {
          key: itemValue(item, index),
          href: item?.href,
          isCurrent: Boolean(item?.current ?? item?.isCurrent),
        },
        itemLabel(item, `Item ${index + 1}`),
      ),
    );
  }

  if (name === "TabList") {
    return asArray(props.items ?? props.tabs).map((item, index) =>
      React.createElement(Tab, {
        key: itemValue(item, index),
        value: itemValue(item, index),
        label: itemLabel(item, `Tab ${index + 1}`),
        isDisabled: Boolean(item?.disabled),
      }),
    );
  }

  if (name === "SegmentedControl") {
    return asArray(props.items ?? props.segments).map((item, index) =>
      React.createElement(SegmentedControlItem, {
        key: itemValue(item, index),
        value: itemValue(item, index),
        label: itemLabel(item, `Option ${index + 1}`),
        isDisabled: Boolean(item?.disabled),
      }),
    );
  }

  if (name === "RadioList") {
    return asArray(props.items).map((item, index) =>
      React.createElement(RadioListItem, {
        key: itemValue(item, index),
        value: itemValue(item, index),
        label: itemLabel(item, `Option ${index + 1}`),
        description: item?.description,
        isDisabled: Boolean(item?.disabled),
      }),
    );
  }

  if (name === "CheckboxList") {
    return asArray(props.items).map((item, index) =>
      React.createElement(CheckboxListItem, {
        key: itemValue(item, index),
        value: itemValue(item, index),
        label: itemLabel(item, `Option ${index + 1}`),
        description: item?.description,
        isDisabled: Boolean(item?.disabled),
      }),
    );
  }

  if (name === "ButtonGroup") {
    return asArray(props.items).map((item, index) =>
      React.createElement(Button, {
        key: itemValue(item, index),
        label: itemLabel(item, `Action ${index + 1}`),
        variant: item?.variant || "secondary",
        isDisabled: Boolean(item?.disabled),
        onClick: () => sendModelAction(model, itemValue(item, index)),
      }),
    );
  }

  if (name === "ToggleButtonGroup") {
    return asArray(props.items).map((item, index) =>
      React.createElement(ToggleButton, {
        key: itemValue(item, index),
        value: itemValue(item, index),
        label: itemLabel(item, `Option ${index + 1}`),
        variant: item?.variant,
        size: item?.size,
        tooltip: item?.tooltip,
        icon: item?.icon ? iconNode(item.icon) : undefined,
        pressedIcon: item?.pressedIcon ? iconNode(item.pressedIcon) : undefined,
        isIconOnly: Boolean(item?.isIconOnly),
        isDisabled: Boolean(item?.disabled ?? item?.isDisabled),
      }),
    );
  }

  return null;
}

function componentChildren(model) {
  const name = String(model.get("component_name") || model.get("component_kind") || "Stack");
  const slots = slotChildren(model);
  if (["Tooltip", "HoverCard", "Popover"].includes(name)) {
    return (slotByKey(model, "trigger") ?? slots ?? textFor(model)) || undefined;
  }
  if (name === "Overlay") {
    return slotByKey(model, "base");
  }
  if (name === "InputGroup") {
    const props = rawProps(model);
    const keyedSlots = keyedSlotChildren(model);
    const children = [
      props.prefix == null ? null : React.createElement(InputGroupText, { key: "__prefix" }, String(props.prefix)),
      ...keyedSlots,
      props.suffix == null ? null : React.createElement(InputGroupText, { key: "__suffix" }, String(props.suffix)),
    ].filter(Boolean);
    return children.length ? children : undefined;
  }
  if (name === "Toolbar") {
    return undefined;
  }
  if (slots) {
    return slots;
  }
  const generated = generatedChildren(model, name);
  if (generated) {
    return generated;
  }
  if (PROP_DRIVEN_COMPONENTS.has(name)) {
    return undefined;
  }
  const text = textFor(model);
  return text || undefined;
}

function AstryxTableView({ model }) {
  const props = modelProps(model);
  const originalProps = rawProps(model);
  const idKey = String(originalProps.idKey ?? "id");
  const data = asArray(originalProps.rows ?? originalProps.data);
  const sortable = Boolean(model.get("sortable"));
  const columns = tableColumns(originalProps.columns, sortable);
  const selected = asArray(model.get("selected")).map(String);
  const selectedSet = React.useMemo(() => new Set(selected), [selected.join("\u0000")]);
  const selects = String(model.get("selects") || "");
  const selectableRows = React.useMemo(
    () => data.filter((row, index) => row?.isSelectable !== false && row?.selectable !== false),
    [data],
  );
  const sortKey = String(model.get("sort_key") || "");
  const sortDirection = tableSortDirectionForAstryx(String(model.get("sort_direction") || ""));
  const sort = sortKey && sortDirection ? [{ sortKey, direction: sortDirection }] : [];
  const hasSortableColumns = columns.some((column) => Boolean(column.sortable));

  const selectionPlugin = useTableSelection({
    getIsItemSelected: (item) => selectedSet.has(tableRowId(item, idKey)),
    onSelectItem: ({ item, isSelected }) => {
      const rowId = tableRowId(item, idKey);
      if (selects === "single") {
        setTableSelection(model, isSelected ? [rowId] : []);
        return;
      }
      const nextSelected = new Set(selectedSet);
      if (isSelected) {
        nextSelected.add(rowId);
      } else {
        nextSelected.delete(rowId);
      }
      setTableSelection(model, [...nextSelected]);
    },
    onSelectAll: ({ isAllSelected }) => {
      if (selects === "single") {
        setTableSelection(model, isAllSelected && selectableRows.length > 0 ? [tableRowId(selectableRows[0], idKey)] : []);
        return;
      }
      setTableSelection(model, isAllSelected ? selectableRows.map((row, index) => tableRowId(row, idKey, index)) : []);
    },
    getIsAllSelected: () =>
      selects === "multiple" &&
      selectableRows.length > 0 &&
      selectableRows.every((row, index) => selectedSet.has(tableRowId(row, idKey, index))),
    getIsIndeterminate: () => {
      if (selects !== "multiple") {
        return false;
      }
      const selectedCount = selectableRows.filter((row, index) => selectedSet.has(tableRowId(row, idKey, index))).length;
      return selectedCount > 0 && selectedCount < selectableRows.length;
    },
    getIsItemSelectable: (item) => item?.isSelectable !== false && item?.selectable !== false,
    getIsItemEnabled: (item) => item?.isEnabled !== false && item?.enabled !== false,
  });
  const sortPlugin = useTableSortable({
    sort,
    onSortChange: (nextSort) => setTableSort(model, nextSort),
    allowUnsortedState: true,
  });
  const plugins = {
    ...(selects === "single" || selects === "multiple" ? { selection: selectionPlugin } : {}),
    ...(sortable || hasSortableColumns ? { sort: sortPlugin } : {}),
  };

  return React.createElement(Table, {
    ...props,
    data: sortedTableData(data, sort),
    columns,
    idKey,
    plugins,
  });
}

function AstryxModelView({ model }) {
  const name = String(model.get("component_name") || model.get("component_kind") || "Stack");
  const mode = useColorMode(String(model.get("color_mode") || "light"));
  const brandKey = JSON.stringify(model.get("brand") ?? {});
  const theme = React.useMemo(() => brandTheme(model.get("brand") ?? {}), [brandKey]);
  const css = React.useMemo(() => themeCSS(model.get("brand") ?? {}, theme), [brandKey, theme]);
  useThemeCSS(theme.name, css);
  useDocumentThemeGuard();
  const draft = useDraft();
  const props = componentProps(model, draft, React.useId());
  const Component = componentFor(name, props);
  const children = componentChildren(model);

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
      name === "Table"
        ? React.createElement(AstryxTableView, { model })
        : React.createElement(Component, props, children),
    ),
  );
}

/**
 * Render each composed child into the slot React laid out for it. Slots that
 * already hold a rendered child are left alone.
 */
async function renderChildren(model, host, rootElement, childSignal, reset) {
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
    if (reset) {
      // React reuses a slot element whose key survived, so the previous child
      // has to be cleared out before a different one renders into it.
      slot.replaceChildren();
    } else if (slot.dataset.anyluminoRendered === "true") {
      continue;
    }
    await renderWidgetRef(model, host, ref, slot, childSignal);
    slot.dataset.anyluminoRendered = "true";
  }
}

export default {
  initialize({ model }) {
    return {
      getComponentName: () => model.get("component_name"),
    };
  },

  async render({ model, el, signal, host }) {
    if (!host?.getWidget && (model.get("widgets") ?? []).length > 0) {
      throw new Error("[anylumino] The current anywidget host does not support widget composition.");
    }

    // Astryx names CSS anchors from React useId values. Every widget is its own
    // React root, and roots restart useId from the same counter, so without a
    // distinct prefix per root the anchor names collide and a popover positions
    // against another widget's trigger.
    const reactRoot = createRoot(el, { identifierPrefix: `al${nextReactRootId()}-` });
    let childController = new AbortController();
    let childKey = childSignature(model);
    let scheduled = false;

    const renderCurrent = () => {
      const nextChildKey = childSignature(model);
      const childrenChanged = nextChildKey !== childKey;
      if (childrenChanged) {
        childController.abort();
        childController = new AbortController();
        childKey = nextChildKey;
      }
      flushSync(() => {
        reactRoot.render(React.createElement(AstryxModelView, { model }));
      });
      void renderChildren(model, host, el, combineSignals(signal, childController.signal), childrenChanged);
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
      "theme",
      "brand",
      "continuous_update",
      "search_mode",
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
