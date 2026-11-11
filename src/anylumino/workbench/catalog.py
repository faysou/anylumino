"""The anylumino components an OpenUI program may use, and the OpenUI library spec built from them."""

from __future__ import annotations

import importlib
import inspect
import re
import types
import typing
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any

import anylumino as al
import anylumino.astryx as ax

# Plotly is optional, so the Plot component exists only where it is installed
try:
    import plotly.graph_objects as go
except ImportError:
    go = None


ROOT = "VBox"
CALLBACK = "Callback"

_STRING = {"type": "string"}
_NUMBER = {"type": "number"}
_BOOLEAN = {"type": "boolean"}
_STRINGS = {"type": "array", "items": _STRING}
_NUMBERS = {"type": "array", "items": _NUMBER}
_ACTION_REF = {"$ref": "#/$defs/ActionExpression"}


class PropKind(StrEnum):
    """What a catalog prop holds."""

    VALUE = "value"
    """A constructor keyword."""
    CHILDREN = "children"
    """A slot of components."""
    ACTION = "action"
    """An OpenUI action."""
    OPTIONS = "options"
    """The object of extra constructor keywords that ends every widget component."""


class ActionEvent(StrEnum):
    """The widget event an action prop binds to."""

    CLICK = "click"
    CHANGE = "change"


@dataclass(frozen=True)
class Prop:
    """One positional prop of a catalog component.

    ``argument`` is the constructor keyword when it differs from the prop name.
    ``event`` is the widget event of an action prop.
    """

    name: str
    schema: dict[str, Any]
    required: bool = False
    kind: PropKind = PropKind.VALUE
    argument: str = ""
    event: ActionEvent | None = None

    @property
    def keyword(self) -> str:
        return self.argument or self.name


@dataclass(frozen=True)
class Component:
    """A catalog component: the OpenUI name, the class it builds, and its props.

    ``module`` is ``al``, ``ax``, or ``go`` for the built-in components, or the
    dotted path of the module that defines ``cls``, such as
    ``"lightweight_charts"`` for a component a notebook skill adds.

    ``fixed`` are constructor keywords generated code always passes, such as
    the ``direction`` of the Astryx stack behind `VBox` and `HBox`.
    """

    name: str
    module: str
    cls: str
    description: str
    props: tuple[Prop, ...]
    fixed: tuple[tuple[str, Any], ...] = ()

    @property
    def factory(self) -> str:
        return f"{self.module}.{self.cls}"

    @property
    def options(self) -> dict[str, Any]:
        """Return the option schemas by keyword, or an empty dict for a component without options."""
        prop = next((prop for prop in self.props if prop.kind == PropKind.OPTIONS), None)

        return prop.schema["properties"] if prop else {}


def _children(argument: str = "widgets", required: bool = True, name: str = "children") -> Prop:
    return Prop(name, {"type": "array", "items": {"$ref": "#/$defs/Component"}}, required, PropKind.CHILDREN, argument)


def _slot(name: str, required: bool = False) -> Prop:
    return _children(name, required, name)


def _change() -> Prop:
    return Prop("on_change", _ACTION_REF, kind=PropKind.ACTION, event=ActionEvent.CHANGE)


_COMPONENTS: tuple[Component, ...] = (
    Component(
        "VBox",
        "ax",
        "Stack",
        "Stacks children top to bottom at their natural size; gap is an Astryx spacing step",
        (_children("children"), Prop("gap", _NUMBER)),
        fixed=(("direction", "vertical"),)
    ),
    Component(
        "HBox",
        "ax",
        "Stack",
        "Places children left to right at their natural size; gap is an Astryx spacing step",
        (_children("children"), Prop("gap", _NUMBER)),
        fixed=(("direction", "horizontal"),)
    ),
    Component(
        "SplitPanel",
        "al",
        "SplitPanel",
        "Resizable panes; sizes are relative weights",
        (
            _children(),
            Prop("orientation", {"type": "string", "enum": ["horizontal", "vertical"]}),
            Prop("sizes", _NUMBERS),
        )
    ),
    Component(
        "TabPanel",
        "al",
        "TabPanel",
        "One tab per child, titled in order",
        (_children(), Prop("titles", _STRINGS))
    ),
    Component("Card", "ax", "Card", "A bordered surface around its children", (_children("children", False),)),
    Component(
        "Heading",
        "ax",
        "Heading",
        "A section heading; level 1 is the largest",
        (Prop("text", _STRING, True), Prop("level", _NUMBER))
    ),
    Component("Text", "ax", "Text", "A run of plain text", (Prop("text", _STRING, True),)),
    Component("Markdown", "ax", "Markdown", "Rendered Markdown text", (Prop("text", _STRING, True),)),
    Component(
        "Button",
        "ax",
        "Button",
        "A button that runs its action when clicked",
        (
            Prop("label", _STRING, True),
            Prop("action", _ACTION_REF, kind=PropKind.ACTION, event=ActionEvent.CLICK),
            Prop("variant", {"type": "string", "enum": ["primary", "secondary", "ghost", "destructive"]}),
        )
    ),
    Component(
        "TextInput",
        "ax",
        "TextInput",
        "A single-line text field; on_change runs with the new text",
        (Prop("label", _STRING), Prop("value", _STRING), Prop("placeholder", _STRING), _change())
    ),
    Component(
        "TextArea",
        "ax",
        "TextArea",
        "A multi-line text field; on_change runs with the new text",
        (Prop("label", _STRING), Prop("value", _STRING), Prop("placeholder", _STRING), Prop("rows", _NUMBER), _change())
    ),
    Component(
        "NumberInput",
        "ax",
        "NumberInput",
        "A number field; on_change runs with the new number",
        (
            Prop("label", _STRING),
            Prop("value", _NUMBER),
            Prop("min", _NUMBER),
            Prop("max", _NUMBER),
            Prop("step", _NUMBER),
            _change(),
        )
    ),
    Component(
        "Selector",
        "ax",
        "Selector",
        "A dropdown of string items; on_change runs with the chosen item",
        (Prop("items", _STRINGS, True), Prop("value", _STRING), Prop("label", _STRING), _change())
    ),
    Component(
        "Slider",
        "ax",
        "Slider",
        "A numeric slider; on_change runs with the new number",
        (
            Prop("label", _STRING),
            Prop("value", _NUMBER),
            Prop("min", _NUMBER),
            Prop("max", _NUMBER),
            Prop("step", _NUMBER),
            _change(),
        )
    ),
    Component(
        "Switch",
        "ax",
        "Switch",
        "An on/off switch; on_change runs with true or false",
        (Prop("label", _STRING), Prop("value", _BOOLEAN), _change())
    ),
    Component(
        "Checkbox",
        "ax",
        "Checkbox",
        "A checkbox; on_change runs with true or false",
        (Prop("label", _STRING), Prop("value", _BOOLEAN), _change())
    ),
    Component(
        "Badge",
        "ax",
        "Badge",
        "A small status label",
        (
            Prop("label", _STRING, True),
            Prop("variant", {"type": "string", "enum": ["neutral", "info", "success", "warning", "error"]}),
        )
    ),
    Component(
        "Table",
        "ax",
        "Table",
        "A table of row objects; columns lists the keys to show",
        (Prop("rows", {"type": "array", "items": {"type": "object"}}, True), Prop("columns", _STRINGS))
    ),
    Component(
        "Tabulator",
        "al",
        "Tabulator",
        "A virtualized data grid of row objects with Tabulator column definitions, such as "
        "{title: \"Last\", field: \"last\", editor: \"number\"}; a callback changes rows with "
        "self.ui.grid.update_rows, add_rows, upsert_rows, or delete_rows. Wherever Tabulator takes a function, "
        "pass {\"$js\": \"function(cell) { return cell.getValue(); }\"}: its JavaScript source runs in the page",
        (Prop("data", {"type": "array", "items": {"type": "object"}}, True), Prop("columns", {"type": "array", "items": {"type": "object"}})),
    ),
    Component(
        "CodeBlock",
        "ax",
        "CodeBlock",
        "Highlighted source code",
        (Prop("code", _STRING, True), Prop("language", _STRING))
    ),
    Component(
        "AppShell",
        "ax",
        "AppShell",
        "An app frame around content, with a TopNav in top_nav and a SideNav in side_nav",
        (_slot("content", True), _slot("top_nav"), _slot("side_nav"), _slot("banner"))
    ),
    Component(
        "Layout",
        "ax",
        "Layout",
        "Content with header, footer, and start and end side panels",
        (_slot("content", True), _slot("header"), _slot("start"), _slot("end"), _slot("footer"))
    ),
    Component(
        "SideNav",
        "ax",
        "SideNav",
        'Side navigation of labels or {label, value, icon, items} records; {type: "section", title, items} '
        "groups them; on_change runs with the selected value",
        (Prop("items", {"type": "array"}, True), Prop("value", _STRING), _change())
    ),
    Component(
        "TopNav",
        "ax",
        "TopNav",
        "Top navigation of labels or {label, value, icon, items} records, where items opens a dropdown; "
        "on_change runs with the selected or clicked value",
        (Prop("items", {"type": "array"}, True), Prop("value", _STRING), _slot("end"), _change())
    ),
    Component(
        "Stepper",
        "ax",
        "Stepper",
        "Ordered steps; value is the zero-based active step",
        (Prop("items", _STRINGS, True), Prop("value", _NUMBER), _change())
    ),
    Component(
        "OverflowList",
        "ax",
        "OverflowList",
        "Buttons that overflow into a More menu; action runs with the clicked item",
        (
            Prop("items", _STRINGS, True),
            Prop("action", _ACTION_REF, kind=PropKind.ACTION, event=ActionEvent.CHANGE),
        )
    ),
    Component(
        "ComplexSelector",
        "ax",
        "ComplexSelector",
        "A selector whose popup holds content; a callback sets self.ui.<name>.value and calls .hide()",
        (Prop("label", _STRING, True), _slot("content", True), Prop("value", _STRING))
    ),
    Component(
        "RichTextEditor",
        "ax",
        "RichTextEditor",
        "A rich text editor; on_change runs with the new Markdown",
        (Prop("label", _STRING, True), Prop("value", _STRING), _change())
    ),
    Component("RichTextView", "ax", "RichTextView", "Read-only rich text rendered from Markdown", (Prop("text", _STRING, True),)),
    Component(
        "Timer",
        "ax",
        "Timer",
        "Elapsed time since it rendered",
        ()
    ),
    Component(
        "Toast",
        "ax",
        "Toast",
        "Notifications that callbacks show with self.ui.<name>.notify(text)",
        (),
    ),
    Component(
        "Indicator",
        "ax",
        "Indicator",
        "A check, checkbox, or radio mark",
        (Prop("value", {"type": "string", "enum": ["unchecked", "checked", "indeterminate"]}),)
    ),
    Component("NavIcon", "ax", "NavIcon", "An icon on an accent circle, such as an app logo", (Prop("icon", _STRING, True),)),
    Component(
        "Plot",
        "go",
        "FigureWidget",
        "An empty Plotly figure that the callbacks fill, such as self.ui.chart.add_traces(...); "
        "layout holds literal Plotly layout keys, such as {height: 320}",
        (Prop("layout", {"type": "object"}),)
    ),
    Component(
        "Widget",
        "",
        "",
        "Mounts the notebook widget stored in the workbench namespace under this name",
        (Prop("name", _STRING, True),),
    ),
)

_MODULES = {"al": al, "ax": ax, "go": go}
def _type_key(annotation: Any) -> Any:
    """Return ``annotation`` in one form for `typing` and `collections.abc` generics, which differ."""
    if isinstance(annotation, (list, tuple)):
        # Such as the parameter list of `Callable[[str], None]`
        return tuple(_type_key(item) for item in annotation)

    origin = typing.get_origin(annotation)

    return annotation if origin is None else (origin, _type_key(typing.get_args(annotation)))


# Literal types of option values, by the Python type that annotates them
_TYPE_SCHEMAS: dict[Any, dict[str, Any]] = {
    _type_key(annotation): schema
    for annotation, schema in (
        (bool, _BOOLEAN),
        (int, _NUMBER),
        (float, _NUMBER),
        (str, _STRING),
        (Iterable[str], _STRINGS),
        (Iterable[int], _NUMBERS),
        (Iterable[Mapping[str, Any]], {"type": "array", "items": {"type": "object"}}),
        (Iterable[Any], {"type": "array"}),
        (Mapping[str, Any], {"type": "object"}),
        (Mapping[str, str], {"type": "object"}),
    )
}


def component_class(component: Component) -> type:
    """Return the class ``component`` builds, importing its module when it is a dotted path."""
    module = _MODULES.get(component.module) or importlib.import_module(component.module)

    return getattr(module, component.cls)


def _with_options(component: Component) -> Component:
    if not component.module:
        return component

    cls = component_class(component)
    taken = {prop.keyword for prop in component.props} | {key for key, _ in component.fixed}
    descriptions = _parameters(inspect.cleandoc(cls.__doc__ or ""))
    types = _parameter_types(cls.__init__)
    properties = {}
    for name, parameter in inspect.signature(cls.__init__).parameters.items():
        if name == "self" or name in taken or parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            continue

        schema = _type_schema(types[name]) if name in types else None
        if schema is not None:
            properties[name] = {**schema, "description": descriptions.get(name, ("", ""))[1]}

    if not properties:
        return component

    schema = {"type": "object", "properties": properties, "additionalProperties": False}

    return replace(component, props=(*component.props, Prop("options", schema, kind=PropKind.OPTIONS)))


def _parameter_types(function: Any) -> dict[str, Any]:
    """Return the resolved annotation of each parameter of ``function``.

    A parameter annotated with a name its module only imports for type
    checking has no resolved type, so it stays out of the options.
    """
    try:
        return typing.get_type_hints(function)
    except Exception:
        types = {}
        for name, annotation in inspect.get_annotations(function).items():
            try:
                types[name] = typing.get_type_hints(_annotated(name, annotation), function.__globals__)[name]
            except Exception:
                continue

        return types


def _annotated(name: str, annotation: Any) -> Any:
    def holder() -> None: ...

    holder.__annotations__ = {name: annotation}

    return holder


# Callables and other Python-only types have no OpenUI literal, so their keywords stay out of options.
# An option enum, such as `Size | str`, allows only the enum's values: the `str` takes the same values.
def _type_schema(annotation: Any) -> dict[str, Any] | None:
    parts = typing.get_args(annotation) if isinstance(annotation, types.UnionType) or typing.get_origin(annotation) is typing.Union else (annotation,)
    parts = [part for part in parts if part is not type(None)]
    option_enums = [part for part in parts if isinstance(part, type) and issubclass(part, StrEnum)]
    if option_enums:
        return {"type": "string", "enum": [member.value for member in option_enums[0]]}

    literals = [value for part in parts if typing.get_origin(part) is typing.Literal for value in typing.get_args(part)]
    if literals:
        return {"type": "string", "enum": [str(value) for value in literals]}

    schemas = []
    for part in parts:
        schema = _TYPE_SCHEMAS.get(_type_key(part))
        if schema is None:
            return None

        if schema not in schemas:
            schemas.append(schema)

    if not schemas:
        return None

    return schemas[0] if len(schemas) == 1 else {"anyOf": schemas}


# Reads the numpydoc ``Parameters`` section as the type text and joined description of each entry.
def _parameters(doc: str) -> dict[str, tuple[str, str]]:
    lines = doc.splitlines()
    try:
        start = lines.index("Parameters") + 2
    except ValueError:
        return {}

    kinds: dict[str, str] = {}
    descriptions: dict[str, list[str]] = {}
    current = None
    for line in lines[start:]:
        if line and not line.startswith(" "):
            match = re.match(r"^(\w+) : (.*)$", line)
            if match is None:
                break

            current = match.group(1)
            kinds[current] = match.group(2)
            descriptions[current] = []
        elif current is not None and line.strip():
            descriptions[current].append(line.strip())

    return {name: (kinds[name], " ".join(text)) for name, text in descriptions.items()}


COMPONENTS: tuple[Component, ...] = tuple(
    _with_options(component) for component in _COMPONENTS if _MODULES.get(component.module, al) is not None
)
CATALOG: dict[str, Component] = {component.name: component for component in COMPONENTS}


def extend(components: Iterable[Component]) -> tuple[Component, ...]:
    """Return the built-in components followed by ``components``, with their options added.

    Raises
    ------
    ValueError
        If a component reuses the name of another component.
    """
    added = tuple(_with_options(component) for component in components)
    names = [component.name for component in (*COMPONENTS, *added)]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"Component names must be unique; {', '.join(duplicates)} is defined twice")

    return (*COMPONENTS, *added)

_CALLBACK_PARAMS = {
    "type": "object",
    "properties": {"handler": _STRING, "context": {}},
    "required": ["handler"],
}
_CALLBACK_DESCRIPTION = "Calls the Python callback named handler with the event and the widgets"


def library_spec(components: Sequence[Component] = COMPONENTS) -> dict[str, Any]:
    """Return the OpenUI LibrarySpec for ``components``, with the `Callback` custom action."""
    defs: dict[str, Any] = {component.name: _component_schema(component) for component in components}
    defs["Component"] = {"anyOf": [{"$ref": f"#/$defs/{component.name}"} for component in components]}
    defs["ActionExpression"] = {
        "anyOf": [
            {
                "type": "object",
                "properties": {"type": {"type": "string", "const": "continue_conversation"}, "context": {}},
                "required": ["type"],
            },
            {"type": "object", "properties": {"type": _STRING, "params": {"type": "object"}}, "required": ["type"]},
        ]
    }
    defs[CALLBACK] = {
        "type": "object",
        "properties": {"type": {"type": "string", "const": CALLBACK}, "params": _CALLBACK_PARAMS},
        "required": ["type", "params"],
    }

    return {
        "id": "anylumino",
        "version": "1.0.0",
        "root": ROOT,
        "schema": {
            "properties": {component.name: {"$ref": f"#/$defs/{component.name}"} for component in components},
            "$defs": defs,
            "actions": {CALLBACK: {"description": _CALLBACK_DESCRIPTION, "params": _CALLBACK_PARAMS}},
        },
        "components": {
            component.name: {"signature": _signature(component), "description": component.description}
            for component in components
        },
        "actions": {
            CALLBACK: {"signature": f"{CALLBACK}(handler: string, context?: any)", "description": _CALLBACK_DESCRIPTION}
        },
    }


def _component_schema(component: Component) -> dict[str, Any]:
    return {
        "type": "object",
        "description": component.description,
        "properties": {prop.name: prop.schema for prop in component.props},
        "required": [prop.name for prop in component.props if prop.required],
    }


def _signature(component: Component) -> str:
    params = ", ".join(
        f"{prop.name}{'' if prop.required else '?'}: {type_name(prop.schema)}" for prop in component.props
    )

    return f"{component.name}({params})"


def type_name(schema: dict[str, Any]) -> str:
    """Return the TypeScript-style type OpenUI signatures use for ``schema``."""
    if schema.get("$ref") == "#/$defs/Component":
        return "Component"

    if schema.get("$ref") == "#/$defs/ActionExpression":
        return "ActionExpression"

    if "enum" in schema:
        return " | ".join(f'"{value}"' for value in schema["enum"])

    if "anyOf" in schema:
        return " | ".join(type_name(option) for option in schema["anyOf"])

    if schema.get("type") == "array":
        return f"{type_name(schema['items'])}[]" if "items" in schema else "any[]"

    return schema.get("type", "any")
