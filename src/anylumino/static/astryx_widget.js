import React from "react";
import { flushSync } from "react-dom";
import { createRoot } from "react-dom/client";
import "@astryxdesign/core/reset.css";
import "@astryxdesign/core/astryx.css";
import "@astryxdesign/theme-neutral/theme.css";
import { AspectRatio } from "@astryxdesign/core/AspectRatio";
import { Avatar } from "@astryxdesign/core/Avatar";
import { Badge } from "@astryxdesign/core/Badge";
import { Banner } from "@astryxdesign/core/Banner";
import { Blockquote } from "@astryxdesign/core/Blockquote";
import { Breadcrumbs, BreadcrumbItem } from "@astryxdesign/core/Breadcrumbs";
import { Button } from "@astryxdesign/core/Button";
import { ButtonGroup } from "@astryxdesign/core/ButtonGroup";
import { Card } from "@astryxdesign/core/Card";
import { Center } from "@astryxdesign/core/Center";
import { CheckboxInput } from "@astryxdesign/core/CheckboxInput";
import { CheckboxList, CheckboxListItem } from "@astryxdesign/core/CheckboxList";
import { ClickableCard } from "@astryxdesign/core/ClickableCard";
import { CodeBlock } from "@astryxdesign/core/CodeBlock";
import { DateInput } from "@astryxdesign/core/DateInput";
import { DateRangeInput } from "@astryxdesign/core/DateRangeInput";
import { DateTimeInput } from "@astryxdesign/core/DateTimeInput";
import { Divider } from "@astryxdesign/core/Divider";
import { EmptyState } from "@astryxdesign/core/EmptyState";
import { Grid } from "@astryxdesign/core/Grid";
import { Icon } from "@astryxdesign/core/Icon";
import { IconButton } from "@astryxdesign/core/IconButton";
import { Item } from "@astryxdesign/core/Item";
import { Kbd } from "@astryxdesign/core/Kbd";
import { Link } from "@astryxdesign/core/Link";
import { List, ListItem } from "@astryxdesign/core/List";
import { Markdown } from "@astryxdesign/core/Markdown";
import { MetadataList, MetadataListItem } from "@astryxdesign/core/MetadataList";
import { MultiSelector } from "@astryxdesign/core/MultiSelector";
import { NumberInput } from "@astryxdesign/core/NumberInput";
import { Pagination } from "@astryxdesign/core/Pagination";
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
import { ToggleButton } from "@astryxdesign/core/ToggleButton";
import { Token } from "@astryxdesign/core/Token";
import { Theme } from "@astryxdesign/core/theme";
import { neutralTheme } from "@astryxdesign/theme-neutral/built";
import {
  combineSignals,
  cssSize,
  removeModelListener,
  renderWidgetRef,
} from "./composition.js";
import "./astryx_widget.css";

const COMPONENTS = {
  AspectRatio,
  Avatar,
  Badge,
  Banner,
  Blockquote,
  Breadcrumbs,
  Button,
  ButtonGroup,
  Card,
  Center,
  CheckboxInput,
  CheckboxList,
  ClickableCard,
  CodeBlock,
  DateInput,
  DateRangeInput,
  DateTimeInput,
  Divider,
  EmptyState,
  Grid,
  Heading,
  Icon,
  IconButton,
  Item,
  Kbd,
  Link,
  List,
  Markdown,
  MetadataList,
  MultiSelector,
  NumberInput,
  Pagination,
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
  Token,
};

const PROP_DRIVEN_COMPONENTS = new Set([
  "Avatar",
  "Badge",
  "Button",
  "CheckboxInput",
  "CodeBlock",
  "DateInput",
  "DateRangeInput",
  "DateTimeInput",
  "Divider",
  "EmptyState",
  "Icon",
  "IconButton",
  "Kbd",
  "MultiSelector",
  "NumberInput",
  "Pagination",
  "ProgressBar",
  "SelectableCard",
  "Selector",
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
]);

const GENERATED_CHILD_COMPONENTS = new Set([
  "Breadcrumbs",
  "ButtonGroup",
  "CheckboxList",
  "List",
  "MetadataList",
  "RadioList",
  "SegmentedControl",
  "TabList",
]);

function modelProps(model) {
  const props = { ...(model.get("props") ?? {}) };
  delete props.children;
  delete props.dangerouslySetInnerHTML;
  delete props.ref;
  delete props.key;
  delete props.items;
  delete props.tabs;
  delete props.segments;
  delete props.metadata;
  return props;
}

function textFor(model) {
  return String(model.get("text") || model.get("label") || model.get("value") || "");
}

function setModelValue(model, value, type = "change") {
  model.set("value", value);
  model.save_changes();
  model.send({ type, value });
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

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function rawProps(model) {
  return { ...(model.get("props") ?? {}) };
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
  return refs.map((_ref, index) =>
    React.createElement("div", {
      className: "anylumino-AstryxChild",
      "data-anylumino-key": keys[index] ?? "",
      "data-anylumino-index": String(index),
      key: `${keys[index] ?? "widget"}-${index}`,
    }),
  );
}

function componentProps(model) {
  const name = String(model.get("component_name") || model.get("component_kind") || "Stack");
  const props = modelProps(model);
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

  if (name === "TextInput") {
    return {
      ...props,
      label: label || "Text input",
      value: String(value ?? ""),
      isDisabled: disabled,
      onChange: (nextValue) => setModelValue(model, nextValue),
    };
  }

  if (name === "TextArea") {
    return {
      ...props,
      label: label || "Text area",
      value: String(value ?? ""),
      isDisabled: disabled,
      onChange: (nextValue) => setStringValue(model, nextValue),
    };
  }

  if (name === "NumberInput") {
    return {
      ...props,
      label: label || "Number",
      value: value == null || value === "" ? null : Number(value),
      isDisabled: disabled,
      onChange: (nextValue) => setNumberValue(model, nextValue),
    };
  }

  if (name === "Slider") {
    return {
      ...props,
      label: label || "Slider",
      value: Array.isArray(value) ? value : Number(value ?? props.min ?? 0),
      isDisabled: disabled,
      onChange: (nextValue) => setModelValue(model, nextValue),
      onChangeEnd: (nextValue) => setModelValue(model, nextValue),
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
      onRemove: props.onRemove ? () => model.send({ type: "click", action: "remove" }) : undefined,
      onClick: props.clickable ? () => model.send({ type: "click" }) : undefined,
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
  return COMPONENTS[name] ?? Stack;
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
        onClick: () => model.send({ type: "click", value: itemValue(item, index) }),
      }),
    );
  }

  return null;
}

function componentChildren(model) {
  const name = String(model.get("component_name") || model.get("component_kind") || "Stack");
  const slots = slotChildren(model);
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
  const mode = String(model.get("color_mode") || "light");
  const props = componentProps(model);
  const Component = componentFor(name, props);
  const children = componentChildren(model);

  return React.createElement(
    Theme,
    { theme: neutralTheme, mode },
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

async function renderChildren(model, host, rootElement, signal, childController) {
  const refs = model.get("widgets") ?? [];
  if (refs.length === 0) {
    return;
  }
  await Promise.resolve();
  const slots = rootElement.querySelectorAll(".anylumino-AstryxChild");
  for (const [index, ref] of refs.entries()) {
    const slot = slots[index];
    if (!slot) {
      continue;
    }
    await renderWidgetRef(model, host, ref, slot, combineSignals(signal, childController.signal));
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

    const reactRoot = createRoot(el);
    let childController = new AbortController();

    const renderCurrent = () => {
      childController.abort();
      childController = new AbortController();
      flushSync(() => {
        reactRoot.render(React.createElement(AstryxModelView, { model }));
      });
      void renderChildren(model, host, el, signal, childController);
    };

    const watched = [
      "component_name",
      "component_kind",
      "widgets",
      "child_keys",
      "text",
      "label",
      "value",
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
    ];

    watched.forEach((name) => model.on(`change:${name}`, renderCurrent));
    signal.addEventListener(
      "abort",
      () => {
        childController.abort();
        watched.forEach((name) => removeModelListener(model, `change:${name}`, renderCurrent));
        reactRoot.unmount();
      },
      { once: true },
    );
    renderCurrent();
  },
};
