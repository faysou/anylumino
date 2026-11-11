import { Badge } from "@astryxdesign/core/Badge";
import { Button } from "@astryxdesign/core/Button";
import { CheckboxInput } from "@astryxdesign/core/CheckboxInput";
import { DateInput } from "@astryxdesign/core/DateInput";
import { DateRangeInput } from "@astryxdesign/core/DateRangeInput";
import { DateTimeInput } from "@astryxdesign/core/DateTimeInput";
import { IconButton } from "@astryxdesign/core/IconButton";
import { Markdown } from "@astryxdesign/core/Markdown";
import { MultiSelector } from "@astryxdesign/core/MultiSelector";
import { NumberInput } from "@astryxdesign/core/NumberInput";
import { PowerSearch } from "@astryxdesign/core/PowerSearch";
import { Selector } from "@astryxdesign/core/Selector";
import { Slider } from "@astryxdesign/core/Slider";
import { Switch } from "@astryxdesign/core/Switch";
import { Heading, Text } from "@astryxdesign/core/Text";
import { TextArea } from "@astryxdesign/core/TextArea";
import { TextInput } from "@astryxdesign/core/TextInput";
import { TimeInput } from "@astryxdesign/core/TimeInput";
import { ToggleButton } from "@astryxdesign/core/ToggleButton";
import { RichTextEditor, RichTextEditorToolbar, markdownToEditorStateJSON } from "@astryxdesign/richtext";
import React from "react";
import { clampIndex } from "../../layout/composition.js";
import { logExponent, logValue } from "../astryx_bridge.mjs";
import { iconNode, itemLabel, itemValue } from "./items.mjs";
import { asArray, continuousUpdate, draftHandlers, rawProps, selectAllOnFocus, setArrayValue, setBooleanValue, setModelValue, setNullableStringValue, setNumberValue, setStringValue, textFor } from "./model.mjs";
import { slotsOnly } from "./slots.mjs";

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

function dateTimeProps({ model, props, label, value, disabled, name }) {
  return {
    ...props,
    label: label || name,
    value: value == null || value === "" ? undefined : String(value),
    isDisabled: disabled,
    onChange: (nextValue) => setNullableStringValue(model, nextValue),
  };
}

export const SPECS = {
  Badge: {
    component: Badge,
    props: ({ model, props, label, variant }) => {
      return {
        ...props,
        label: label || textFor(model),
        variant: variant || props.variant || "neutral",
      };
    },
    children: slotsOnly,
  },
  Button: {
    component: Button,
    props: ({ model, props, label, variant, disabled }) => {
      return {
        ...props,
        label: label || "Button",
        variant: variant || "secondary",
        isDisabled: disabled,
        onClick: () => model.send({ type: "click" }),
      };
    },
    children: slotsOnly,
  },
  CheckboxInput: {
    component: CheckboxInput,
    props: ({ model, props, label, value, disabled }) => {
      return {
        ...props,
        label: label || "Checkbox",
        value: value === "indeterminate" ? "indeterminate" : Boolean(value),
        isDisabled: disabled,
        onChange: (nextValue) => setModelValue(model, Boolean(nextValue)),
      };
    },
    children: slotsOnly,
  },
  DateInput: {
    component: DateInput,
    props: dateTimeProps,
    children: slotsOnly,
  },
  DateRangeInput: {
    component: DateRangeInput,
    props: ({ model, props, label, value, disabled }) => {
      return {
        ...props,
        label: label || "Date range",
        value: value ?? null,
        isDisabled: disabled,
        onChange: (nextValue) => setModelValue(model, nextValue),
      };
    },
    children: slotsOnly,
  },
  DateTimeInput: {
    component: DateTimeInput,
    props: dateTimeProps,
    children: slotsOnly,
  },
  Heading: {
    component: Heading,
    props: ({ props }) => {
      return {
        ...props,
        level: Number(props.level ?? 3),
      };
    },
  },
  IconButton: {
    component: IconButton,
    props: ({ model, props, label, variant, disabled }) => {
      return {
        ...props,
        label: label || "Button",
        icon: iconNode(props.icon || model.get("icon") || "close"),
        variant: variant || props.variant || "secondary",
        isDisabled: disabled,
        onClick: () => model.send({ type: "click" }),
      };
    },
    children: slotsOnly,
  },
  LogSlider: {
    component: Slider,
    reserved: ["base", "minExponent", "maxExponent", "labelPosition", "labelWidth"],
    labelRow: true,
    props: ({ model, props, label, disabled, draft, isContinuous, editedValue }) => {
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
    },
    children: slotsOnly,
  },
  MultiSelector: {
    component: MultiSelector,
    reserved: ["labelPosition", "labelWidth"],
    labelRow: true,
    props: ({ model, props, label, value, disabled }) => {
      return {
        ...props,
        label: label || "Multi selector",
        value: asArray(value),
        isDisabled: disabled,
        onChange: (nextValue) => setArrayValue(model, nextValue),
      };
    },
    children: slotsOnly,
  },
  NumberInput: {
    component: NumberInput,
    props: ({ model, props, label, disabled, draft, isContinuous, editedValue }) => {
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
    },
    children: slotsOnly,
  },
  PowerSearch: {
    component: PowerSearch,
    props: ({ model, props, label, value, disabled }) => {
      return {
        ...props,
        label: label || props.label || "Search",
        filters: asArray(value),
        isDisabled: disabled,
        onChange: (filters) => setArrayValue(model, filters),
      };
    },
    children: slotsOnly,
  },
  RichTextEditor: { view: AstryxRichTextEditorView },
  SelectionSlider: {
    component: Slider,
    reserved: ["options", "marks", "labelPosition", "labelWidth"],
    labelRow: true,
    props: ({ model, props, label, disabled, draft, isContinuous, editedValue }) => {
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
    },
    children: slotsOnly,
  },
  Selector: {
    component: Selector,
    reserved: ["labelPosition", "labelWidth"],
    labelRow: true,
    props: ({ model, props, label, value, disabled }) => {
      return {
        ...props,
        label: label || "Selector",
        value: value == null ? (props.hasClear ? null : undefined) : String(value),
        isDisabled: disabled,
        onChange: (nextValue) => setModelValue(model, nextValue),
      };
    },
    children: slotsOnly,
  },
  Slider: {
    component: Slider,
    reserved: ["labelPosition", "labelWidth"],
    labelRow: true,
    props: ({ model, props, label, disabled, draft, isContinuous, editedValue }) => {
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
    },
    children: slotsOnly,
  },
  Switch: {
    component: Switch,
    props: ({ model, props, label, value, disabled }) => {
      return {
        ...props,
        label: label || "Switch",
        value: Boolean(value),
        isDisabled: disabled,
        onChange: (nextValue) => setModelValue(model, Boolean(nextValue)),
      };
    },
    children: slotsOnly,
  },
  Text: {
    component: Text,
    props: ({ props }) => {
      return props;
    },
  },
  TextArea: {
    component: TextArea,
    props: ({ model, props, label, disabled, draft, isContinuous, editedValue }) => {
      return {
        ...props,
        label: label || "Text area",
        value: String(editedValue ?? ""),
        isDisabled: disabled,
        onChange: (nextValue) => setStringValue(model, nextValue),
        ...(isContinuous ? {} : draftHandlers(model, draft)),
      };
    },
    children: slotsOnly,
  },
  TextInput: {
    component: TextInput,
    reserved: ["labelPosition", "labelWidth"],
    labelRow: true,
    props: ({ model, props, label, disabled, draft, isContinuous, editedValue }) => {
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
    },
    children: slotsOnly,
  },
  TimeInput: {
    component: TimeInput,
    props: dateTimeProps,
    children: slotsOnly,
  },
  ToggleButton: {
    component: ToggleButton,
    props: ({ model, props, label, value, disabled }) => {
      return {
        ...props,
        label: label || "Toggle",
        isPressed: Boolean(value),
        isDisabled: disabled,
        onPressedChange: (nextValue) => setBooleanValue(model, nextValue),
      };
    },
    children: slotsOnly,
  },
};
