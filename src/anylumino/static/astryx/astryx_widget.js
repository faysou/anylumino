import React from "react";
import { flushSync } from "react-dom";
import { createRoot } from "react-dom/client";
import "@astryxdesign/core/reset.css";
import "@astryxdesign/core/astryx.css";
import "@astryxdesign/theme-neutral/theme.css";
import { AlertDialog } from "@astryxdesign/core/AlertDialog";
import { AppShell } from "@astryxdesign/core/AppShell";
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
import { Carousel } from "@astryxdesign/core/Carousel";
import { Center } from "@astryxdesign/core/Center";
import {
  ChatComposer,
  ChatLayout,
  ChatMessage,
  ChatMessageBubble,
  ChatMessageList,
  ChatMessageMetadata,
  ChatSystemMessage,
  ChatToolCalls,
} from "@astryxdesign/core/Chat";
import { CheckboxInput } from "@astryxdesign/core/CheckboxInput";
import { CheckboxList, CheckboxListItem } from "@astryxdesign/core/CheckboxList";
import { ClickableCard } from "@astryxdesign/core/ClickableCard";
import { Citation } from "@astryxdesign/core/Citation";
import { Code } from "@astryxdesign/core/Code";
import { CodeBlock } from "@astryxdesign/core/CodeBlock";
import { Collapsible, CollapsibleGroup } from "@astryxdesign/core/Collapsible";
import { CommandPalette } from "@astryxdesign/core/CommandPalette";
import { ComplexSelector } from "@astryxdesign/core/ComplexSelector";
import { ContextMenu } from "@astryxdesign/core/ContextMenu";
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
import { CheckboxIndicator, CheckIndicator, RadioIndicator } from "@astryxdesign/core/Indicator";
import { InputGroup, InputGroupText } from "@astryxdesign/core/InputGroup";
import { Item } from "@astryxdesign/core/Item";
import { Kbd } from "@astryxdesign/core/Kbd";
import { LayerProvider } from "@astryxdesign/core/Layer";
import { Layout, LayoutContent, LayoutFooter, LayoutHeader, LayoutPanel } from "@astryxdesign/core/Layout";
import { Link } from "@astryxdesign/core/Link";
import { Lightbox } from "@astryxdesign/core/Lightbox";
import { List, ListItem } from "@astryxdesign/core/List";
import { Markdown } from "@astryxdesign/core/Markdown";
import { MetadataList, MetadataListItem } from "@astryxdesign/core/MetadataList";
import { MoreMenu } from "@astryxdesign/core/MoreMenu";
import { MultiSelector } from "@astryxdesign/core/MultiSelector";
import { NavIcon } from "@astryxdesign/core/NavIcon";
import { NavHeadingMenu, NavHeadingMenuItem } from "@astryxdesign/core/NavMenu";
import { NumberInput } from "@astryxdesign/core/NumberInput";
import { Outline } from "@astryxdesign/core/Outline";
import { OverflowList } from "@astryxdesign/core/OverflowList";
import { Overlay } from "@astryxdesign/core/Overlay";
import { Pagination } from "@astryxdesign/core/Pagination";
import { Popover } from "@astryxdesign/core/Popover";
import { PowerSearch } from "@astryxdesign/core/PowerSearch";
import { ProgressBar } from "@astryxdesign/core/ProgressBar";
import { RadioList, RadioListItem } from "@astryxdesign/core/RadioList";
import { ResizeHandle, useResizable } from "@astryxdesign/core/Resizable";
import { ScrollableArea } from "@astryxdesign/core/ScrollableArea";
import { Section } from "@astryxdesign/core/Section";
import { SegmentedControl, SegmentedControlItem } from "@astryxdesign/core/SegmentedControl";
import { SelectableCard } from "@astryxdesign/core/SelectableCard";
import { SideNav, SideNavHeading, SideNavItem, SideNavSection } from "@astryxdesign/core/SideNav";
import { Selector } from "@astryxdesign/core/Selector";
import { Skeleton } from "@astryxdesign/core/Skeleton";
import { Slider } from "@astryxdesign/core/Slider";
import { Spinner } from "@astryxdesign/core/Spinner";
import { HStack, Stack, VStack } from "@astryxdesign/core/Stack";
import { StatusDot } from "@astryxdesign/core/StatusDot";
import { Step, Stepper } from "@astryxdesign/core/Stepper";
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
import { Timer } from "@astryxdesign/core/Timer";
import { Timestamp } from "@astryxdesign/core/Timestamp";
import { useToast } from "@astryxdesign/core/Toast";
import { ToggleButton, ToggleButtonGroup } from "@astryxdesign/core/ToggleButton";
import { Token } from "@astryxdesign/core/Token";
import { Tokenizer } from "@astryxdesign/core/Tokenizer";
import { Toolbar } from "@astryxdesign/core/Toolbar";
import { Tooltip } from "@astryxdesign/core/Tooltip";
import { TopNav, TopNavHeading, TopNavItem, TopNavMenu } from "@astryxdesign/core/TopNav";
import { TreeList } from "@astryxdesign/core/TreeList";
import { Typeahead, createStaticSource } from "@astryxdesign/core/Typeahead";
import { Theme, defineTheme, generateThemeCSS } from "@astryxdesign/core/theme";
import { neutralTheme } from "@astryxdesign/theme-neutral/built";
import {
  RichTextEditor,
  RichTextEditorToolbar,
  RichTextView,
  markdownToEditorStateJSON,
} from "@astryxdesign/richtext";
import "@astryxdesign/richtext/richtext.css";
import {
  clampIndex,
  combineSignals,
  cssSize,
  notifyNodeVisible,
  removeModelListener,
  renderWidgetRef,
} from "../layout/composition.js";
import {
  chatMessages,
  childSignature,
  fractionsWithPane,
  logExponent,
  logValue,
  modelProps,
  observeJupyterLabTheme,
  paneFractions,
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
  AppShell,
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
  Carousel,
  Center,
  Chat: ChatLayout,
  CheckboxInput,
  CheckboxList,
  Citation,
  ClickableCard,
  Code,
  CodeBlock,
  Collapsible,
  CommandPalette,
  ContextMenu,
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
  HStack,
  Heading,
  Icon,
  IconButton,
  Indicator: AstryxIndicator,
  InputGroup,
  Item,
  Kbd,
  Layout,
  Link,
  Lightbox,
  List,
  Markdown,
  MetadataList,
  MoreMenu,
  MultiSelector,
  NavIcon,
  NumberInput,
  Outline,
  OverflowList,
  Overlay,
  Pagination,
  Popover,
  PowerSearch,
  ProgressBar,
  RadioList,
  RichTextView,
  Section,
  SegmentedControl,
  SelectableCard,
  Selector,
  SideNav,
  Skeleton,
  Slider,
  Spinner,
  Stack,
  StatusDot,
  Stepper,
  Switch,
  Table,
  TabList,
  Text,
  TextArea,
  TextInput,
  Thumbnail,
  TimeInput,
  Timer,
  Timestamp,
  ToggleButton,
  ToggleButtonGroup,
  Token,
  Tokenizer,
  Toolbar,
  Tooltip,
  TopNav,
  TreeList,
  Typeahead,
  VStack,
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
  "Indicator",
  "Lightbox",
  "Kbd",
  "MultiSelector",
  "MoreMenu",
  "NavIcon",
  "NumberInput",
  "Outline",
  "Pagination",
  "PowerSearch",
  "ProgressBar",
  "RichTextView",
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
  "Timer",
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
  "OverflowList",
  "RadioList",
  "SegmentedControl",
  "SideNav",
  "Stepper",
  "TabList",
  "ToggleButtonGroup",
  "TopNav",
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

function slotChild(model, key, index, hidden = false) {
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
 * Select the current content when a field gains focus, so clicking into a
 * value and typing replaces it instead of merging with the old text. The
 * timeout lets the browser finish placing the caret before the selection.
 */
function selectAllOnFocus(event) {
  const input = event?.target;
  if (input && typeof input.select === "function") {
    setTimeout(() => input.select(), 0);
  }
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
        ? ["options", "marks", "labelPosition", "labelWidth"]
        : name === "LogSlider"
          ? ["base", "minExponent", "maxExponent", "labelPosition", "labelWidth"]
          : ["Slider", "TextInput", "Selector", "MultiSelector"].includes(name)
            ? ["labelPosition", "labelWidth"]
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
    const { selectOnFocus, ...inputProps } = props;
    return {
      ...inputProps,
      label: label || "Text input",
      value: String(editedValue ?? ""),
      isDisabled: disabled,
      onChange: (nextValue) => setStringValue(model, nextValue),
      ...(selectOnFocus ? { onFocus: selectAllOnFocus } : {}),
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
    const { selectOnFocus, ...inputProps } = props;
    return {
      ...inputProps,
      label: label || "Number",
      value: editedValue == null || editedValue === "" ? null : Number(editedValue),
      isDisabled: disabled,
      onChange: (nextValue) => setNumberValue(model, nextValue),
      ...(selectOnFocus === false ? {} : { onFocus: selectAllOnFocus }),
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
      onPageSizeChange: props.pageSizeOptions
        ? (pageSize) => sendModelAction(model, pageSize, "pageSize")
        : undefined,
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

  if (name === "ContextMenu") {
    return {
      ...props,
      items: menuItems(model, rawProps(model).items),
      onOpenChange: (isOpen) => setModelOpen(model, isOpen),
    };
  }

  if (name === "PowerSearch") {
    return {
      ...props,
      label: label || props.label || "Search",
      filters: asArray(value),
      isDisabled: disabled,
      onChange: (filters) => setArrayValue(model, filters),
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

  if (name === "Indicator") {
    return { ...props, state: String(value || "checked"), isDisabled: disabled };
  }

  if (name === "NavIcon") {
    return { ...props, icon: iconNode(props.icon) };
  }

  if (name === "RichTextView") {
    return { ...props, value: markdownToEditorStateJSON(textFor(model)) };
  }

  if (name === "Stepper") {
    const { isNavigable, ...stepperProps } = props;
    return {
      ...stepperProps,
      label: props.label || undefined,
      activeStep: Number(value ?? 0),
      onStepClick: isNavigable ? (index) => setNumberValue(model, index) : undefined,
    };
  }

  if (name === "OverflowList") {
    const { size, label: _label, ...listProps } = props;
    const items = asArray(rawProps(model).items);
    return {
      ...listProps,
      overflowRenderer: (overflow) => React.createElement(MoreMenu, {
        label: label || "More",
        size,
        items: menuItems(model, overflow.map(({ index }) => items[index])),
      }),
    };
  }

  if (name === "SideNav") {
    const { heading, subheading, icon, menu, ...navProps } = props;
    return {
      ...navProps,
      header: heading
        ? React.createElement(SideNavHeading, {
          heading: String(heading),
          subheading: subheading ?? undefined,
          icon: icon ? React.createElement(NavIcon, { icon: iconNode(icon) }) : undefined,
          menu: navHeadingMenu(model, menu),
        })
        : undefined,
    };
  }

  if (name === "TopNav") {
    const { heading, subheading, icon, menu, ...navProps } = props;
    return {
      ...navProps,
      label: props.label || undefined,
      heading: heading || icon
        ? React.createElement(TopNavHeading, {
          heading: heading ?? undefined,
          subheading: subheading ?? undefined,
          logo: icon ? React.createElement(NavIcon, { icon: iconNode(icon) }) : undefined,
          menu: navHeadingMenu(model, menu),
        })
        : undefined,
      endContent: slotByKey(model, "end"),
    };
  }

  if (name === "AppShell") {
    return {
      mobileNav: false,
      ...props,
      topNav: slotByKey(model, "top_nav"),
      sideNav: slotByKey(model, "side_nav"),
      banner: slotByKey(model, "banner"),
    };
  }

  if (name === "Layout") {
    const { startWidth, endWidth, ...layoutProps } = props;
    const header = slotByKey(model, "header");
    const start = slotByKey(model, "start");
    const end = slotByKey(model, "end");
    const footer = slotByKey(model, "footer");
    return {
      ...layoutProps,
      header: header && React.createElement(LayoutHeader, null, header),
      start: start && React.createElement(LayoutPanel, { width: startWidth }, start),
      content: React.createElement(LayoutContent, null, slotByKey(model, "content")),
      end: end && React.createElement(LayoutPanel, { width: endWidth }, end),
      footer: footer && React.createElement(LayoutFooter, null, footer),
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

  if (name === "OverflowList") {
    return asArray(props.items).map((item, index) =>
      React.createElement(Button, {
        key: itemValue(item, index),
        label: itemLabel(item, `Action ${index + 1}`),
        icon: iconNode(item?.icon),
        variant: item?.variant || "secondary",
        size: props.size,
        isDisabled: Boolean(item?.disabled ?? item?.isDisabled),
        onClick: () => sendModelAction(model, itemValue(item, index)),
      }),
    );
  }

  if (name === "Stepper") {
    return asArray(props.items).map((item, index) =>
      React.createElement(Step, {
        key: index,
        step: index,
        label: itemLabel(item, `Step ${index + 1}`),
        description: item?.description,
        status: item?.status,
        isDisabled: Boolean(item?.disabled),
        isOptional: Boolean(item?.optional),
      }),
    );
  }

  if (name === "SideNav") {
    return sideNavItems(model, props.items, String(model.get("value") ?? ""));
  }

  if (name === "TopNav") {
    const selected = String(model.get("value") ?? "");
    return asArray(props.items).map((item, index) => {
      const value = itemValue(item, index);
      if (item?.items) {
        return React.createElement(TopNavMenu, {
          key: value,
          label: itemLabel(item, `Menu ${index + 1}`),
          items: asArray(item.items).map((entry, entryIndex) => ({
            title: itemLabel(entry, `Item ${entryIndex + 1}`),
            description: entry?.description,
            onClick: () => sendModelAction(model, itemValue(entry, entryIndex)),
          })),
        });
      }
      return React.createElement(TopNavItem, {
        key: value,
        label: itemLabel(item, `Item ${index + 1}`),
        icon: iconNode(item?.icon),
        isSelected: value === selected,
        isDisabled: Boolean(item?.disabled),
        onClick: () => setStringValue(model, value),
      });
    });
  }

  return null;
}

function sideNavItems(model, items, selected) {
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

function navHeadingMenu(model, entries) {
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

function AstryxIndicator({ kind, ...props }) {
  const Mark = kind === "check" ? CheckIndicator : kind === "radio" ? RadioIndicator : CheckboxIndicator;
  return React.createElement(Mark, props);
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
  if (name === "Toolbar" || name === "Layout") {
    return undefined;
  }
  if (name === "AppShell") {
    return slotByKey(model, "content");
  }
  if (name === "TopNav") {
    return generatedChildren(model, name);
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

function AstryxChatView({ model }) {
  const props = modelProps(model);
  const isStreaming = Boolean(model.get("is_streaming"));
  const messages = chatMessages(model.get("messages"));
  const lastIndex = messages.length - 1;
  const rows = messages.map((message, index) => {
    if (message.role === "system") {
      return React.createElement(ChatSystemMessage, { key: message.key }, message.content);
    }
    const metadata = message.status || message.isStopped
      ? React.createElement(ChatMessageMetadata, {
        status: message.status,
        footer: message.isStopped ? "Stopped" : undefined,
      })
      : undefined;
    return React.createElement(
      ChatMessage,
      { key: message.key, sender: message.role },
      React.createElement(
        ChatMessageBubble,
        { metadata },
        React.createElement(Markdown, { isStreaming: isStreaming && index === lastIndex }, message.content),
      ),
      message.toolCalls.length > 0 ? React.createElement(ChatToolCalls, { calls: message.toolCalls }) : null,
    );
  });
  const composer = React.createElement(ChatComposer, {
    placeholder: String(model.get("placeholder") || "") || undefined,
    isDisabled: Boolean(model.get("disabled")),
    isStopShown: isStreaming,
    onSubmit: (value) => model.send({ type: "submit", value }),
    onStop: () => model.send({ type: "stop" }),
  });
  return React.createElement(
    ChatLayout,
    { ...props, composer, style: { height: "100%", ...props.style } },
    React.createElement(ChatMessageList, { isStreaming }, rows),
  );
}

function panelChildren(model) {
  const count = (model.get("widgets") ?? []).length;
  const keys = model.get("child_keys") ?? [];
  const titles = model.get("titles") ?? [];
  return {
    count,
    keys: Array.from({ length: count }, (_, index) => String(keys[index] ?? "")),
    titles: Array.from({ length: count }, (_, index) => String(titles[index] || keys[index] || `Item ${index + 1}`)),
  };
}

function setSelectedIndex(model, index) {
  model.set("selected_index", index);
  model.save_changes();
}

function axisSize(node, horizontal) {
  if (!node) {
    return 0;
  }
  return horizontal ? node.clientWidth : node.clientHeight;
}

function useMeasuredSize(ref, horizontal) {
  const [size, setSize] = React.useState(0);
  React.useLayoutEffect(() => {
    const node = ref.current;
    if (!node) {
      return undefined;
    }
    const update = () => setSize(axisSize(node, horizontal));
    update();
    const observer = new ResizeObserver(update);
    observer.observe(node);
    return () => observer.disconnect();
  }, [ref, horizontal]);
  return size;
}

/**
 * Tab and stacked panels show one child at a time. A child mounts the first
 * time it is selected and then stays mounted but hidden, so switching back
 * keeps its state instead of rendering it again.
 */
function AstryxSelectedPanelView({ model }) {
  const name = String(model.get("component_name"));
  const props = modelProps(model);
  const { count, keys, titles } = panelChildren(model);
  const selected = clampIndex(Number(model.get("selected_index") ?? 0), count);
  const visited = React.useRef(new Set());
  visited.current.add(selected);
  const contentRef = React.useRef(null);
  React.useEffect(() => {
    const slot = contentRef.current && ownSlots(model, contentRef.current).get(String(selected));
    if (slot) {
      notifyNodeVisible(slot);
    }
  }, [model, selected]);

  const slots = [];
  for (let index = 0; index < count; index += 1) {
    if (visited.current.has(index)) {
      slots.push(slotChild(model, keys[index], index, index !== selected));
    }
  }
  const content = React.createElement("div", { ref: contentRef, className: "anylumino-PanelContent" }, slots);
  if (name !== "TabPanel") {
    return content;
  }
  const tabs = React.createElement(
    TabList,
    {
      value: keys[selected] ?? "",
      onChange: (nextValue) => setSelectedIndex(model, Math.max(0, keys.indexOf(String(nextValue)))),
      size: props.size,
      layout: props.layout,
      hasDivider: props.hasDivider,
    },
    keys.map((key, index) => React.createElement(Tab, { key: `${key}-${index}`, value: key, label: titles[index] })),
  );
  return React.createElement(VStack, { gap: props.gap ?? 2 }, tabs, content);
}

function AstryxAccordionView({ model }) {
  const props = modelProps(model);
  const { keys, titles } = panelChildren(model);
  const isMultiple = props.type === "multiple";
  const value = model.get("value");
  const openKeys = isMultiple
    ? asArray(value).map(String)
    : (value == null || value === "" ? [] : [String(value)]);
  const contentRef = React.useRef(null);
  const openSignature = openKeys.join(" ");
  React.useEffect(() => {
    if (!contentRef.current) {
      return;
    }
    const slots = ownSlots(model, contentRef.current);
    for (const key of openKeys) {
      const slot = slots.get(String(keys.indexOf(key)));
      if (slot) {
        notifyNodeVisible(slot);
      }
    }
  }, [model, openSignature]);

  const sections = keys.map((key, index) => React.createElement(
    Collapsible,
    { key: `${key}-${index}`, value: key, trigger: titles[index] },
    slotChild(model, key, index),
  ));
  return React.createElement(
    "div",
    { ref: contentRef, className: "anylumino-PanelContent" },
    React.createElement(
      CollapsibleGroup,
      {
        type: isMultiple ? "multiple" : "single",
        value: isMultiple ? openKeys : (openKeys[0] ?? ""),
        onChange: (next) => setModelValue(model, isMultiple ? asArray(next).map(String) : (next == null ? "" : String(next))),
        hasDividers: props.hasDividers ?? true,
        density: props.density,
      },
      sections,
    ),
  );
}

function AstryxScrollBoxView({ model }) {
  const props = modelProps(model);
  return React.createElement(
    ScrollableArea,
    {
      axis: props.axis ?? "block",
      label: String(model.get("label") || props.label || "Scrollable content"),
      role: props.role,
      overscroll: props.overscroll,
      width: props.width ?? cssSize(model.get("width"), undefined),
      height: props.height ?? cssSize(model.get("height"), undefined),
      maxWidth: props.maxWidth,
      minHeight: props.minHeight,
      padding: props.padding,
      paddingInline: props.paddingInline,
      paddingBlock: props.paddingBlock,
    },
    React.createElement(VStack, { gap: props.gap ?? 2 }, keyedSlotChildren(model)),
  );
}

/**
 * Every pane but the last owns a resizable region and the handle after it; the
 * last pane fills what is left. Pane sizes come from `sizes` as fractions of
 * the measured panel, and a drag writes the fractions back.
 */
function AstryxSplitPanelView({ model, mountChildren }) {
  const props = modelProps(model);
  const horizontal = props.orientation !== "vertical";
  const { count, keys } = panelChildren(model);
  const fractions = paneFractions(model.get("sizes"), count);
  const containerRef = React.useRef(null);
  const basis = useMeasuredSize(containerRef, horizontal);
  React.useEffect(() => {
    if (basis > 0) {
      mountChildren();
    }
  }, [basis, count, mountChildren]);

  const onPaneSize = (index, size) => {
    const current = axisSize(containerRef.current, horizontal);
    if (current <= 0) {
      return;
    }
    model.set("sizes", fractionsWithPane(paneFractions(model.get("sizes"), count), index, size / current));
    model.save_changes();
  };
  const handleProps = {
    hasDivider: props.hasDivider ?? true,
    isAlwaysVisible: props.isAlwaysVisible,
    label: props.label,
  };

  const panes = [];
  if (basis > 0) {
    for (let index = 0; index < count; index += 1) {
      const slot = slotChild(model, keys[index], index);
      const key = `${keys[index]}-${index}`;
      if (index === count - 1) {
        panes.push(React.createElement("div", { key, className: "anylumino-SplitPane anylumino-SplitPane-fill" }, slot));
      } else {
        panes.push(React.createElement(AstryxSplitPane, {
          key,
          index,
          fraction: fractions[index],
          basis,
          horizontal,
          minSize: props.minSize,
          handleProps,
          onPaneSize,
        }, slot));
      }
    }
  }
  return React.createElement(
    "div",
    { ref: containerRef, className: `anylumino-SplitPanel anylumino-SplitPanel-${horizontal ? "horizontal" : "vertical"}` },
    panes,
  );
}

function AstryxSplitPane({ index, fraction, basis, horizontal, minSize, handleProps, onPaneSize, children }) {
  const direction = horizontal ? "horizontal" : "vertical";
  const target = Math.round(fraction * basis);
  const region = useResizable({
    direction,
    defaultSize: target,
    minSize: minSize ?? 80,
    onSizeChange: (size) => onPaneSize(index, size),
  });
  React.useEffect(() => {
    if (Math.abs(target - region.size) > 1) {
      region.resize(target);
    }
  }, [target]);
  return React.createElement(
    React.Fragment,
    null,
    React.createElement("div", { className: "anylumino-SplitPane", style: { flex: `0 0 ${region.size}px` } }, children),
    React.createElement(ResizeHandle, { direction, resizable: region.props, ...handleProps }),
  );
}

function AstryxResponsivePanelView({ model }) {
  const props = modelProps(model);
  const containerRef = React.useRef(null);
  const width = useMeasuredSize(containerRef, true);
  const wide = width >= Number(props.breakpoint ?? 760);
  const direction = wide ? (props.wideDirection ?? "horizontal") : (props.narrowDirection ?? "vertical");
  React.useEffect(() => {
    if (containerRef.current) {
      notifyNodeVisible(containerRef.current);
    }
  }, [direction]);
  return React.createElement(
    "div",
    { ref: containerRef, className: "anylumino-PanelContent anylumino-ResponsivePanel" },
    React.createElement(Stack, { direction, gap: props.gap ?? 2, width: "100%" }, keyedSlotChildren(model)),
  );
}

function AstryxComplexSelectorView({ model, props }) {
  const handleRef = React.useRef(null);
  const isOpen = Boolean(model.get("is_open"));
  React.useEffect(() => {
    const handle = handleRef.current;
    if (handle && handle.isOpen() !== isOpen) {
      if (isOpen) {
        handle.open();
      } else {
        handle.close();
      }
    }
  }, [isOpen]);
  const value = model.get("value");
  return React.createElement(
    ComplexSelector,
    {
      ...props,
      value,
      handleRef,
      triggerLabel: props.triggerLabel ?? (value == null || value === "" ? undefined : String(value)),
      isDisabled: Boolean(model.get("disabled")),
      onOpenChange: (nextOpen) => {
        if (nextOpen !== Boolean(model.get("is_open"))) {
          setModelOpen(model, nextOpen);
        }
      },
    },
    () => slotByKey(model, "content"),
  );
}

/**
 * The value syncs as Markdown. The editor keeps its own state, so a value
 * assigned from Python replaces the editor content, and `sent` holds the last
 * Markdown either side produced to keep that from echoing back.
 */
function AstryxRichTextEditorView({ model, props }) {
  const editorRef = React.useRef(null);
  const value = String(model.get("value") ?? "");
  const sent = React.useRef(value);
  const [defaultValue] = React.useState(() => markdownToEditorStateJSON(value));
  React.useEffect(() => {
    const editor = editorRef.current?.getEditor();
    if (!editor || value === sent.current) {
      return;
    }
    editor.setEditorState(editor.parseEditorState(markdownToEditorStateJSON(value)));
    sent.current = editorRef.current.getMarkdown();
  }, [value]);
  const commit = () => {
    const markdown = editorRef.current?.getMarkdown() ?? "";
    if (markdown !== sent.current) {
      sent.current = markdown;
      setStringValue(model, markdown);
    }
  };
  const { hasToolbar, ...editorProps } = props;
  return React.createElement(RichTextEditor, {
    ...editorProps,
    ref: editorRef,
    label: String(model.get("label") || props.label || "Rich text"),
    isDisabled: Boolean(model.get("disabled")),
    defaultValue,
    toolbar: hasToolbar === false ? undefined : React.createElement(RichTextEditorToolbar),
    onChange: () => {
      if (continuousUpdate(model)) {
        commit();
      }
    },
    onBlur: commit,
  });
}

function AstryxToastView({ model, props }) {
  const { position, maxVisible, inset } = props;
  return React.createElement(
    LayerProvider,
    { toast: { position, maxVisible, inset } },
    React.createElement(AstryxToastListener, { model }),
  );
}

function AstryxToastListener({ model }) {
  const showToast = useToast();
  React.useEffect(() => {
    const dismissals = new Map();
    const onMessage = (content) => {
      const id = String(content?.id ?? "");
      if (content?.type === "toast") {
        const dismiss = showToast({
          body: String(content.body ?? ""),
          type: content.toast_type,
          isAutoHide: content.auto_hide ?? undefined,
          autoHideDuration: content.duration ?? undefined,
          uniqueID: id,
          onHide: () => {
            if (dismissals.get(id) === dismiss) {
              dismissals.delete(id);
            }
          },
        });
        dismissals.set(id, dismiss);
      } else if (content?.type === "toast-dismiss") {
        dismissals.get(id)?.();
      }
    };
    model.on("msg:custom", onMessage);
    return () => removeModelListener(model, "msg:custom", onMessage);
  }, [model, showToast]);
  return null;
}

const MODEL_VIEWS = {
  ComplexSelector: AstryxComplexSelectorView,
  RichTextEditor: AstryxRichTextEditorView,
  Toast: AstryxToastView,
};

const PANEL_VIEWS = {
  AccordionPanel: AstryxAccordionView,
  ResponsivePanel: AstryxResponsivePanelView,
  ScrollBox: AstryxScrollBoxView,
  SplitPanel: AstryxSplitPanelView,
  StackedPanel: AstryxSelectedPanelView,
  TabPanel: AstryxSelectedPanelView,
};

function AstryxModelView({ model, styleRoot, mountChildren }) {
  const name = String(model.get("component_name") || model.get("component_kind") || "Stack");
  const mode = useColorMode(String(model.get("color_mode") || "light"));
  const brandKey = JSON.stringify(model.get("brand") ?? {});
  const theme = React.useMemo(() => brandTheme(model.get("brand") ?? {}), [brandKey]);
  const css = React.useMemo(() => themeCSS(model.get("brand") ?? {}, theme), [brandKey, theme]);
  useThemeCSS(theme.name, css, styleRoot);
  useDocumentThemeGuard();
  const draft = useDraft();
  const props = componentProps(model, draft, React.useId());
  const PanelView = PANEL_VIEWS[name];
  const ModelView = MODEL_VIEWS[name];
  const Component = PanelView || ModelView ? null : componentFor(name, props);
  const children = PanelView || ModelView ? undefined : componentChildren(model);
  const component = PanelView
    ? React.createElement(PanelView, { model, mountChildren })
    : ModelView
      ? React.createElement(ModelView, { model, props })
      : name === "Table"
        ? React.createElement(AstryxTableView, { model })
        : name === "Chat"
          ? React.createElement(AstryxChatView, { model })
          : React.createElement(Component, props, children);
  const horizontalLabel = Component !== null
    && [Slider, TextInput, Selector, MultiSelector].includes(Component)
    && rawProps(model).labelPosition === "left"
    && !props.isLabelHidden;

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
    } else if (slot.dataset.anyluminoRendered === "true" || slot.dataset.anyluminoRendering === "true") {
      continue;
    }
    // A panel view can request a mount while a model change already runs one,
    // so a slot is claimed before its child renders.
    slot.dataset.anyluminoRendering = "true";
    try {
      await renderWidgetRef(model, host, ref, slot, childSignal);
      slot.dataset.anyluminoRendered = "true";
    } finally {
      delete slot.dataset.anyluminoRendering;
    }
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
    let scheduled = false;

    // Panel views create slots from their own state, such as a measured pane
    // size, and ask for the children to be mounted once those slots exist.
    const mountChildren = () => {
      void renderChildren(model, host, el, combineSignals(signal, childController.signal), false);
    };

    const renderCurrent = () => {
      const nextChildKey = childSignature(model);
      const childrenChanged = nextChildKey !== childKey;
      if (childrenChanged) {
        childController.abort();
        childController = new AbortController();
        childKey = nextChildKey;
      }
      flushSync(() => {
        reactRoot.render(React.createElement(AstryxModelView, { model, styleRoot, mountChildren }));
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
      "theme",
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
