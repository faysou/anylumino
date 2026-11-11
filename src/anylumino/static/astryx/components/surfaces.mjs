import { AlertDialog } from "@astryxdesign/core/AlertDialog";
import { AppShell } from "@astryxdesign/core/AppShell";
import { AspectRatio } from "@astryxdesign/core/AspectRatio";
import { Avatar } from "@astryxdesign/core/Avatar";
import { AvatarGroup, AvatarGroupOverflow } from "@astryxdesign/core/AvatarGroup";
import { BreadcrumbItem, Breadcrumbs } from "@astryxdesign/core/Breadcrumbs";
import { Button } from "@astryxdesign/core/Button";
import { ButtonGroup } from "@astryxdesign/core/ButtonGroup";
import { Calendar } from "@astryxdesign/core/Calendar";
import { Card } from "@astryxdesign/core/Card";
import { Carousel } from "@astryxdesign/core/Carousel";
import { Center } from "@astryxdesign/core/Center";
import { CheckboxList, CheckboxListItem } from "@astryxdesign/core/CheckboxList";
import { Citation } from "@astryxdesign/core/Citation";
import { ClickableCard } from "@astryxdesign/core/ClickableCard";
import { Code } from "@astryxdesign/core/Code";
import { Collapsible } from "@astryxdesign/core/Collapsible";
import { CommandPalette } from "@astryxdesign/core/CommandPalette";
import { ComplexSelector } from "@astryxdesign/core/ComplexSelector";
import { ContextMenu } from "@astryxdesign/core/ContextMenu";
import { Dialog } from "@astryxdesign/core/Dialog";
import { Divider } from "@astryxdesign/core/Divider";
import { DropdownMenu } from "@astryxdesign/core/DropdownMenu";
import { Field } from "@astryxdesign/core/Field";
import { FieldStatus } from "@astryxdesign/core/FieldStatus";
import { FileInput } from "@astryxdesign/core/FileInput";
import { FormLayout } from "@astryxdesign/core/FormLayout";
import { Grid } from "@astryxdesign/core/Grid";
import { HoverCard } from "@astryxdesign/core/HoverCard";
import { InputGroup, InputGroupText } from "@astryxdesign/core/InputGroup";
import { Item } from "@astryxdesign/core/Item";
import { Layout, LayoutContent, LayoutFooter, LayoutHeader, LayoutPanel } from "@astryxdesign/core/Layout";
import { Lightbox } from "@astryxdesign/core/Lightbox";
import { List, ListItem } from "@astryxdesign/core/List";
import { MetadataList, MetadataListItem } from "@astryxdesign/core/MetadataList";
import { MoreMenu } from "@astryxdesign/core/MoreMenu";
import { NavIcon } from "@astryxdesign/core/NavIcon";
import { Outline } from "@astryxdesign/core/Outline";
import { OverflowList } from "@astryxdesign/core/OverflowList";
import { Overlay } from "@astryxdesign/core/Overlay";
import { Popover } from "@astryxdesign/core/Popover";
import { RadioList, RadioListItem } from "@astryxdesign/core/RadioList";
import { Section } from "@astryxdesign/core/Section";
import { SegmentedControl, SegmentedControlItem } from "@astryxdesign/core/SegmentedControl";
import { SelectableCard } from "@astryxdesign/core/SelectableCard";
import { SideNav, SideNavHeading } from "@astryxdesign/core/SideNav";
import { Step, Stepper } from "@astryxdesign/core/Stepper";
import { Tab, TabList } from "@astryxdesign/core/TabList";
import { ToggleButton, ToggleButtonGroup } from "@astryxdesign/core/ToggleButton";
import { Tokenizer } from "@astryxdesign/core/Tokenizer";
import { Toolbar } from "@astryxdesign/core/Toolbar";
import { Tooltip } from "@astryxdesign/core/Tooltip";
import { TopNav, TopNavHeading, TopNavItem, TopNavMenu } from "@astryxdesign/core/TopNav";
import { TreeList } from "@astryxdesign/core/TreeList";
import { Typeahead } from "@astryxdesign/core/Typeahead";
import React from "react";
import { sendModelAction, setModelOpen, toggleGroupValue } from "../astryx_bridge.mjs";
import { iconNode, itemLabel, itemValue, menuItems, navHeadingMenu, sideNavItems } from "./items.mjs";
import { asArray, fileInputValue, rawProps, setArrayValue, setBooleanValue, setItemArrayValue, setItemValue, setModelValue, setNumberValue, setStringValue, textFor } from "./model.mjs";
import { rememberItems, searchSourceFor, searchableItems, selectedSearchItem, selectedSearchItems } from "./search.mjs";
import { keyedSlotChildren, slotByKey, slotChildren, slotsOnly } from "./slots.mjs";

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

// The File objects last picked in each FileInput model, which Python cannot hold.
const pickedFiles = new WeakMap();

export const SPECS = {
  AlertDialog: {
    component: AlertDialog,
    props: ({ model, props, label }) => {
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
    },
    children: slotsOnly,
  },
  AppShell: {
    component: AppShell,
    traits: ["variant"],
    props: ({ model, props }) => {
      return {
        mobileNav: false,
        ...props,
        topNav: slotByKey(model, "top_nav"),
        sideNav: slotByKey(model, "side_nav"),
        banner: slotByKey(model, "banner"),
      };
    },
    children: ({ model }) => slotByKey(model, "content"),
  },
  AspectRatio: { component: AspectRatio },
  AvatarGroup: {
    component: AvatarGroup,
    reserved: ["items", "tabs", "segments", "metadata"],
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
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
    })(ctx),
  },
  Breadcrumbs: {
    component: Breadcrumbs,
    traits: ["label", "variant"],
    reserved: ["items", "tabs", "segments", "metadata"],
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
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
    })(ctx),
  },
  ButtonGroup: {
    component: ButtonGroup,
    traits: ["label", "disabled"],
    reserved: ["items", "tabs", "segments", "metadata"],
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
      return asArray(props.items).map((item, index) =>
        React.createElement(Button, {
          key: itemValue(item, index),
          label: itemLabel(item, `Action ${index + 1}`),
          variant: item?.variant || "secondary",
          isDisabled: Boolean(item?.disabled),
          onClick: () => sendModelAction(model, itemValue(item, index)),
        }),
      );
    })(ctx),
  },
  Calendar: {
    component: Calendar,
    props: ({ model, props, value }) => {
      return {
        ...props,
        value: value == null || value === "" ? undefined : value,
        onChange: (nextValue) => setModelValue(model, nextValue),
      };
    },
    children: slotsOnly,
  },
  Card: {
    component: Card,
    traits: ["variant"],
  },
  Carousel: { component: Carousel },
  Center: { component: Center },
  CheckboxList: {
    component: CheckboxList,
    reserved: ["items", "tabs", "segments", "metadata"],
    props: ({ model, props, label, value, disabled }) => {
      return {
        ...props,
        label: label || "Options",
        value: asArray(value),
        isDisabled: disabled,
        onChange: (nextValue) => setArrayValue(model, nextValue),
      };
    },
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
      return asArray(props.items).map((item, index) =>
        React.createElement(CheckboxListItem, {
          key: itemValue(item, index),
          value: itemValue(item, index),
          label: itemLabel(item, `Option ${index + 1}`),
          description: item?.description,
          isDisabled: Boolean(item?.disabled),
        }),
      );
    })(ctx),
  },
  Citation: {
    component: Citation,
    props: ({ model, props, label, variant, value }) => {
      return {
        ...props,
        source: props.source ?? { title: label || textFor(model) },
        number: Number(value ?? props.number ?? 1),
        variant: variant || props.variant || "number",
      };
    },
    children: slotsOnly,
  },
  ClickableCard: {
    component: ClickableCard,
    props: ({ model, props, label, variant, disabled }) => {
      return {
        ...props,
        label: label || "Card",
        variant: variant || props.variant || "default",
        isDisabled: disabled,
        onClick: () => model.send({ type: "click" }),
      };
    },
  },
  Code: { component: Code },
  Collapsible: {
    component: Collapsible,
    props: ({ model, props, label }) => {
      return {
        ...props,
        trigger: props.trigger || label || textFor(model) || "Details",
        isOpen: Boolean(model.get("is_open")),
        onOpenChange: (isOpen) => setModelOpen(model, isOpen),
      };
    },
  },
  CommandPalette: {
    component: CommandPalette,
    reserved: ["items"],
    props: ({ model, props, label, value }) => {
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
    },
    children: slotsOnly,
  },
  ComplexSelector: {
    view: AstryxComplexSelectorView,
    traits: ["label", "variant"],
  },
  ContextMenu: {
    component: ContextMenu,
    traits: ["disabled"],
    props: ({ model, props }) => {
      return {
        ...props,
        items: menuItems(model, rawProps(model).items),
        onOpenChange: (isOpen) => setModelOpen(model, isOpen),
      };
    },
  },
  Dialog: {
    component: Dialog,
    traits: ["variant"],
    props: ({ model, props }) => {
      return {
        ...props,
        isInline: props.isInline ?? true,
        isOpen: Boolean(model.get("is_open")),
        onOpenChange: (isOpen) => setModelOpen(model, isOpen),
      };
    },
    children: slotsOnly,
  },
  Divider: {
    component: Divider,
    traits: ["label", "variant"],
    children: slotsOnly,
  },
  DropdownMenu: {
    component: DropdownMenu,
    props: ({ model, props, label, variant, disabled }) => {
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
    },
    children: slotsOnly,
  },
  Field: {
    component: Field,
    props: ({ props, label, disabled, elementId }) => {
      return {
        ...props,
        label: label || props.label || "Field",
        inputID: props.inputID || props.inputId || elementId,
        isDisabled: disabled || props.isDisabled,
      };
    },
  },
  FieldStatus: {
    component: FieldStatus,
    traits: ["variant"],
    props: ({ model, props, label }) => {
      return {
        ...props,
        type: props.type || "success",
        message: label || props.message || textFor(model),
      };
    },
    children: slotsOnly,
  },
  FileInput: {
    component: FileInput,
    props: ({ model, props, label, value, disabled }) => {
      const isMultiple = Boolean(props.isMultiple || props.multiple);
      return {
        ...props,
        label: label || props.label || "File",
        // Python holds only file metadata, so the picked File objects stay here to show the
        // selection, until Python clears the value.
        value: value == null || (isMultiple && value.length === 0) ? null : (pickedFiles.get(model) ?? null),
        isDisabled: disabled,
        isMultiple,
        onChange: (files) => {
          pickedFiles.set(model, files ?? null);
          setModelValue(model, fileInputValue(files, isMultiple));
        },
      };
    },
    children: slotsOnly,
  },
  FormLayout: {
    component: FormLayout,
    props: ({ props }) => {
      return {
        direction: "vertical",
        ...props,
      };
    },
  },
  Grid: { component: Grid },
  HoverCard: {
    component: HoverCard,
    props: ({ model, props, label }) => {
      const result = {
        ...props,
        content: props.content ?? slotByKey(model, "content") ?? label ?? textFor(model),
      };
      if (props.isOpen !== undefined) {
        result.isOpen = Boolean(model.get("is_open"));
        result.onOpenChange = (isOpen) => setModelOpen(model, isOpen);
      }
      return result;
    },
    children: ({ model }) => (slotByKey(model, "trigger") ?? slotChildren(model) ?? textFor(model)) || undefined,
  },
  InputGroup: {
    component: InputGroup,
    props: ({ props, label, disabled }) => {
      return {
        ...props,
        label: label || props.label || "Input group",
        isDisabled: disabled || props.isDisabled,
      };
    },
    children: ({ model }) => {
      const props = rawProps(model);
      const keyedSlots = keyedSlotChildren(model);
      const children = [
        props.prefix == null ? null : React.createElement(InputGroupText, { key: "__prefix" }, String(props.prefix)),
        ...keyedSlots,
        props.suffix == null ? null : React.createElement(InputGroupText, { key: "__suffix" }, String(props.suffix)),
      ].filter(Boolean);
      return children.length ? children : undefined;
    },
  },
  Item: { component: Item },
  Layout: {
    component: Layout,
    props: ({ model, props }) => {
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
    },
    children: () => undefined,
  },
  Lightbox: {
    component: Lightbox,
    props: ({ model, props, value }) => {
      return {
        ...props,
        isOpen: Boolean(model.get("is_open")),
        index: Number(value ?? 0),
        onOpenChange: (isOpen) => setModelOpen(model, isOpen),
        onIndexChange: (nextIndex) => setNumberValue(model, nextIndex),
      };
    },
    children: slotsOnly,
  },
  List: {
    component: List,
    reserved: ["items", "tabs", "segments", "metadata"],
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
      return asArray(props.items).map((item, index) =>
        React.createElement(ListItem, {
          key: itemValue(item, index),
          label: itemLabel(item, `Item ${index + 1}`),
          description: item && typeof item === "object" ? item.description : undefined,
          isSelected: Boolean(item?.selected),
          isDisabled: Boolean(item?.disabled),
        }),
      );
    })(ctx),
  },
  MetadataList: {
    component: MetadataList,
    traits: ["label"],
    reserved: ["items", "tabs", "segments", "metadata"],
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
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
    })(ctx),
  },
  MoreMenu: {
    component: MoreMenu,
    traits: ["variant"],
    props: ({ model, props, label, disabled }) => {
      return {
        ...props,
        label: label || props.label || "More options",
        isDisabled: disabled,
        isMenuOpen: Boolean(model.get("is_open")),
        items: menuItems(model, rawProps(model).items),
        onOpenChange: (isOpen) => setModelOpen(model, isOpen),
      };
    },
    children: slotsOnly,
  },
  Outline: {
    component: Outline,
    traits: ["label"],
    props: ({ model, props, value }) => {
      const originalProps = rawProps(model);
      return {
        ...props,
        items: asArray(originalProps.items),
        activeId: value || props.activeId,
        onActiveIdChange: (nextValue) => setStringValue(model, nextValue),
      };
    },
    children: slotsOnly,
  },
  OverflowList: {
    component: OverflowList,
    reserved: ["items", "tabs", "segments", "metadata"],
    props: ({ model, props, label }) => {
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
    },
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
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
    })(ctx),
  },
  Overlay: {
    component: Overlay,
    props: ({ model, props }) => {
      const result = {
        ...props,
        content: props.content ?? slotByKey(model, "content"),
      };
      if (props.isOpen !== undefined) {
        result.isOpen = Boolean(model.get("is_open"));
      }
      return result;
    },
    children: ({ model }) => slotByKey(model, "base"),
  },
  Popover: {
    component: Popover,
    props: ({ model, props, label }) => {
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
    },
    children: ({ model }) => (slotByKey(model, "trigger") ?? slotChildren(model) ?? textFor(model)) || undefined,
  },
  RadioList: {
    component: RadioList,
    reserved: ["items", "tabs", "segments", "metadata"],
    props: ({ model, props, label, value, disabled }) => {
      return {
        ...props,
        label: label || "Options",
        value: String(value ?? ""),
        isDisabled: disabled,
        onChange: (nextValue) => setStringValue(model, nextValue),
      };
    },
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
      return asArray(props.items).map((item, index) =>
        React.createElement(RadioListItem, {
          key: itemValue(item, index),
          value: itemValue(item, index),
          label: itemLabel(item, `Option ${index + 1}`),
          description: item?.description,
          isDisabled: Boolean(item?.disabled),
        }),
      );
    })(ctx),
  },
  Section: {
    component: Section,
    traits: ["variant"],
  },
  SegmentedControl: {
    component: SegmentedControl,
    reserved: ["items", "tabs", "segments", "metadata"],
    props: ({ model, props, label, value, disabled }) => {
      return {
        ...props,
        label: label || "Segmented control",
        value: String(value ?? ""),
        isDisabled: disabled,
        onChange: (nextValue) => setStringValue(model, nextValue),
      };
    },
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
      return asArray(props.items ?? props.segments).map((item, index) =>
        React.createElement(SegmentedControlItem, {
          key: itemValue(item, index),
          value: itemValue(item, index),
          label: itemLabel(item, `Option ${index + 1}`),
          isDisabled: Boolean(item?.disabled),
        }),
      );
    })(ctx),
  },
  SelectableCard: {
    component: SelectableCard,
    props: ({ model, props, label, variant, value, disabled }) => {
      return {
        ...props,
        label: label || "Selectable card",
        isSelected: Boolean(value),
        isDisabled: disabled,
        variant: variant || props.variant || "default",
        onChange: (nextValue) => setBooleanValue(model, nextValue),
      };
    },
    children: slotsOnly,
  },
  SideNav: {
    component: SideNav,
    reserved: ["items", "tabs", "segments", "metadata"],
    props: ({ model, props }) => {
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
    },
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
      return sideNavItems(model, props.items, String(model.get("value") ?? ""));
    })(ctx),
  },
  Stepper: {
    component: Stepper,
    traits: ["label"],
    reserved: ["items", "tabs", "segments", "metadata"],
    props: ({ model, props, value }) => {
      const { isNavigable, ...stepperProps } = props;
      return {
        ...stepperProps,
        label: props.label || undefined,
        activeStep: Number(value ?? 0),
        onStepClick: isNavigable ? (index) => setNumberValue(model, index) : undefined,
      };
    },
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
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
    })(ctx),
  },
  TabList: {
    component: TabList,
    reserved: ["items", "tabs", "segments", "metadata"],
    props: ({ model, props, value }) => {
      return {
        ...props,
        value: String(value ?? ""),
        onChange: (nextValue) => setStringValue(model, nextValue),
      };
    },
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
      return asArray(props.items ?? props.tabs).map((item, index) =>
        React.createElement(Tab, {
          key: itemValue(item, index),
          value: itemValue(item, index),
          label: itemLabel(item, `Tab ${index + 1}`),
          isDisabled: Boolean(item?.disabled),
        }),
      );
    })(ctx),
  },
  ToggleButtonGroup: {
    component: ToggleButtonGroup,
    reserved: ["items", "tabs", "segments", "metadata"],
    props: ({ model, props, label, value, disabled }) => {
      const isMultiple = props.type === "multiple";
      return {
        ...props,
        label: label || "Toggle buttons",
        type: isMultiple ? "multiple" : "single",
        value: toggleGroupValue(value, isMultiple),
        isDisabled: disabled,
        onChange: (nextValue) => setModelValue(model, nextValue),
      };
    },
    children: (ctx) => slotChildren(ctx.model) ?? (({ model }) => {
      const props = rawProps(model);
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
    })(ctx),
  },
  Tokenizer: {
    component: Tokenizer,
    reserved: ["items"],
    props: ({ model, props, label, value, disabled }) => {
      const items = searchableItems(rawProps(model).items);
      return {
        ...props,
        label: label || props.label || "Tokenizer",
        value: selectedSearchItems(model, items, value),
        searchSource: searchSourceFor(model, items),
        isDisabled: disabled,
        onChange: (nextItems) => {
          rememberItems(model, nextItems);
          setItemArrayValue(model, nextItems);
        },
      };
    },
    children: slotsOnly,
  },
  Toolbar: {
    component: Toolbar,
    traits: ["variant"],
    props: ({ model, props, label }) => {
      return {
        ...props,
        label: label || props.label || "Toolbar",
        startContent: props.startContent ?? slotByKey(model, "start"),
        centerContent: props.centerContent ?? slotByKey(model, "center"),
        endContent: props.endContent ?? slotByKey(model, "end"),
      };
    },
    children: () => undefined,
  },
  Tooltip: {
    component: Tooltip,
    props: ({ model, props, label }) => {
      const result = {
        ...props,
        content: props.content ?? slotByKey(model, "content") ?? label ?? textFor(model),
      };
      if (props.isOpen !== undefined) {
        result.isOpen = Boolean(model.get("is_open"));
        result.onOpenChange = (isOpen) => setModelOpen(model, isOpen);
      }
      return result;
    },
    children: ({ model }) => (slotByKey(model, "trigger") ?? slotChildren(model) ?? textFor(model)) || undefined,
  },
  TopNav: {
    component: TopNav,
    traits: ["label"],
    reserved: ["items", "tabs", "segments", "metadata"],
    props: ({ model, props }) => {
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
    },
    children: ({ model }) => {
      const props = rawProps(model);
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
    },
  },
  TreeList: {
    component: TreeList,
    props: ({ model, props }) => {
      const originalProps = rawProps(model);
      return {
        ...props,
        items: asArray(originalProps.items),
      };
    },
    children: slotsOnly,
  },
  Typeahead: {
    component: Typeahead,
    reserved: ["items"],
    props: ({ model, props, label, value, disabled }) => {
      const items = searchableItems(rawProps(model).items);
      return {
        ...props,
        label: label || props.label || "Typeahead",
        value: selectedSearchItem(model, items, value),
        searchSource: searchSourceFor(model, items),
        isDisabled: disabled,
        onChange: (item) => {
          rememberItems(model, [item]);
          setItemValue(model, item);
        },
        onOpenChange: (isOpen) => setModelOpen(model, isOpen),
      };
    },
    children: slotsOnly,
  },
};
