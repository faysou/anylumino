import { Avatar } from "@astryxdesign/core/Avatar";
import { Banner } from "@astryxdesign/core/Banner";
import { Blockquote } from "@astryxdesign/core/Blockquote";
import { CodeBlock } from "@astryxdesign/core/CodeBlock";
import { EmptyState } from "@astryxdesign/core/EmptyState";
import { Icon } from "@astryxdesign/core/Icon";
import { InternationalizationProvider } from "@astryxdesign/core/i18n";
import { CheckIndicator, CheckboxIndicator, RadioIndicator } from "@astryxdesign/core/Indicator";
import { Kbd } from "@astryxdesign/core/Kbd";
import { LayerProvider } from "@astryxdesign/core/Layer";
import { Link } from "@astryxdesign/core/Link";
import { Markdown } from "@astryxdesign/core/Markdown";
import { NavIcon } from "@astryxdesign/core/NavIcon";
import { Pagination } from "@astryxdesign/core/Pagination";
import { ProgressBar } from "@astryxdesign/core/ProgressBar";
import { Skeleton } from "@astryxdesign/core/Skeleton";
import { Spinner } from "@astryxdesign/core/Spinner";
import { StatusDot } from "@astryxdesign/core/StatusDot";
import { Table, pixel, proportional, useTableSelection, useTableSortable } from "@astryxdesign/core/Table";
import { Thumbnail } from "@astryxdesign/core/Thumbnail";
import { Timer } from "@astryxdesign/core/Timer";
import { Timestamp } from "@astryxdesign/core/Timestamp";
import { useToast } from "@astryxdesign/core/Toast";
import { Token } from "@astryxdesign/core/Token";
import { RichTextView, markdownToEditorStateJSON } from "@astryxdesign/richtext";
import React from "react";
import { removeModelListener } from "../../layout/composition.js";
import { modelProps, sendModelAction } from "../astryx_bridge.mjs";
import { iconNode } from "./items.mjs";
import { asArray, rawProps, setNumberValue, textFor } from "./model.mjs";
import { slotsOnly } from "./slots.mjs";

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

  // Astryx reads the select-all checkbox label from its message catalog, not from a prop.
  const overrides = { en: { "@astryx.table.selection.selectAllRows": String(model.get("select_all_label") || "Select all rows") } };
  return React.createElement(
    InternationalizationProvider,
    { locale: "en", overrides },
    React.createElement(Table, {
      ...props,
      data: sortedTableData(data, sort),
      columns,
      idKey,
      plugins,
    }),
  );
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

function AstryxIndicator({ kind, ...props }) {
  const Mark = kind === "check" ? CheckIndicator : kind === "radio" ? RadioIndicator : CheckboxIndicator;
  return React.createElement(Mark, props);
}

export const SPECS = {
  Avatar: {
    component: Avatar,
    props: ({ model, props, label }) => {
      return {
        ...props,
        name: label || props.name || textFor(model),
      };
    },
    children: slotsOnly,
  },
  Banner: {
    component: Banner,
    props: ({ model, props }) => {
      return {
        ...props,
        onDismiss: props.isDismissable
          ? () => sendModelAction(model, undefined, "dismiss")
          : undefined,
      };
    },
  },
  Blockquote: { component: Blockquote },
  CodeBlock: {
    component: CodeBlock,
    children: slotsOnly,
  },
  EmptyState: {
    component: EmptyState,
    children: slotsOnly,
  },
  Icon: {
    component: Icon,
    props: ({ model, props }) => {
      return {
        ...props,
        icon: props.icon || model.get("icon") || textFor(model) || "circle",
      };
    },
    children: slotsOnly,
  },
  Indicator: {
    component: AstryxIndicator,
    props: ({ props, value, disabled }) => {
      return { ...props, state: String(value || "checked"), isDisabled: disabled };
    },
    children: slotsOnly,
  },
  Kbd: {
    component: Kbd,
    children: slotsOnly,
  },
  Link: {
    component: Link,
    traits: ["disabled"],
  },
  Markdown: { component: Markdown },
  NavIcon: {
    component: NavIcon,
    traits: ["icon"],
    props: ({ props }) => {
      return { ...props, icon: iconNode(props.icon) };
    },
    children: slotsOnly,
  },
  Pagination: {
    component: Pagination,
    traits: ["label", "variant", "disabled"],
    props: ({ model, props, value }) => {
      return {
        ...props,
        page: Number(value ?? props.page ?? 1),
        onChange: (nextValue) => setNumberValue(model, nextValue),
        onPageSizeChange: props.pageSizeOptions
          ? (pageSize) => sendModelAction(model, pageSize, "pageSize")
          : undefined,
      };
    },
    children: slotsOnly,
  },
  ProgressBar: {
    component: ProgressBar,
    props: ({ model, props, label, variant, value, disabled }) => {
      return {
        ...props,
        label: label || textFor(model) || "Progress",
        value: value == null ? props.value : Number(value),
        variant: variant || props.variant || "accent",
        isDisabled: disabled,
      };
    },
    children: slotsOnly,
  },
  RichTextView: {
    component: RichTextView,
    props: ({ model, props }) => {
      return { ...props, value: markdownToEditorStateJSON(textFor(model)) };
    },
    children: slotsOnly,
  },
  Skeleton: {
    component: Skeleton,
    children: slotsOnly,
  },
  Spinner: {
    component: Spinner,
    traits: ["label"],
    children: slotsOnly,
  },
  StatusDot: {
    component: StatusDot,
    props: ({ model, props, label, variant }) => {
      return {
        ...props,
        label: label || textFor(model) || "Status",
        variant: variant || props.variant || "neutral",
      };
    },
    children: slotsOnly,
  },
  Table: {
    view: AstryxTableView,
    children: slotsOnly,
  },
  Thumbnail: {
    component: Thumbnail,
    traits: ["label"],
    props: ({ model, props, disabled }) => {
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
    },
    children: slotsOnly,
  },
  Timer: {
    component: Timer,
    children: slotsOnly,
  },
  Timestamp: {
    component: Timestamp,
    props: ({ model, props, value }) => {
      return {
        ...props,
        value: value ?? props.value ?? textFor(model),
      };
    },
    children: slotsOnly,
  },
  Toast: { view: AstryxToastView },
  Token: {
    component: Token,
    traits: ["disabled"],
    props: ({ model, props, label }) => {
      return {
        ...props,
        label: label || textFor(model),
        onRemove: props.onRemove ? () => sendModelAction(model, undefined, "remove") : undefined,
        onClick: props.clickable ? () => sendModelAction(model, undefined, "click") : undefined,
      };
    },
    children: slotsOnly,
  },
};
