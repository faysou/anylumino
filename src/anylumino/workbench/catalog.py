"""The anylumino components an OpenUI program may use, and the OpenUI library spec built from them."""

from __future__ import annotations

import inspect
import re
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
    """A catalog component: the OpenUI name, the anylumino class it builds, and its props.

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


def _children(argument: str = "widgets", required: bool = True) -> Prop:
    return Prop("children", {"type": "array", "items": {"$ref": "#/$defs/Component"}}, required, PropKind.CHILDREN, argument)


def _change() -> Prop:
    return Prop("on_change", _ACTION_REF, kind=PropKind.ACTION, event=ActionEvent.CHANGE)


_COMPONENTS: tuple[Component, ...] = (
    Component(
        "VBox",
        "ax",
        "Stack",
        "Stacks children top to bottom at their natural size; gap is an Astryx spacing step",
        (_children("children"), Prop("gap", _NUMBER)),
        fixed=(("direction", "vertical"),),
    ),
    Component(
        "HBox",
        "ax",
        "Stack",
        "Places children left to right at their natural size; gap is an Astryx spacing step",
        (_children("children"), Prop("gap", _NUMBER)),
        fixed=(("direction", "horizontal"),),
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
        ),
    ),
    Component(
        "TabPanel",
        "al",
        "TabPanel",
        "One tab per child, titled in order",
        (_children(), Prop("titles", _STRINGS)),
    ),
    Component("Card", "ax", "Card", "A bordered surface around its children", (_children("children", False),)),
    Component(
        "Heading",
        "ax",
        "Heading",
        "A section heading; level 1 is the largest",
        (Prop("text", _STRING, True), Prop("level", _NUMBER)),
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
        ),
    ),
    Component(
        "TextInput",
        "ax",
        "TextInput",
        "A single-line text field; on_change runs with the new text",
        (Prop("label", _STRING), Prop("value", _STRING), Prop("placeholder", _STRING), _change()),
    ),
    Component(
        "TextArea",
        "ax",
        "TextArea",
        "A multi-line text field; on_change runs with the new text",
        (Prop("label", _STRING), Prop("value", _STRING), Prop("placeholder", _STRING), Prop("rows", _NUMBER), _change()),
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
        ),
    ),
    Component(
        "Selector",
        "ax",
        "Selector",
        "A dropdown of string items; on_change runs with the chosen item",
        (Prop("items", _STRINGS, True), Prop("value", _STRING), Prop("label", _STRING), _change()),
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
        ),
    ),
    Component(
        "Switch",
        "ax",
        "Switch",
        "An on/off switch; on_change runs with true or false",
        (Prop("label", _STRING), Prop("value", _BOOLEAN), _change()),
    ),
    Component(
        "Checkbox",
        "ax",
        "Checkbox",
        "A checkbox; on_change runs with true or false",
        (Prop("label", _STRING), Prop("value", _BOOLEAN), _change()),
    ),
    Component(
        "Badge",
        "ax",
        "Badge",
        "A small status label",
        (
            Prop("label", _STRING, True),
            Prop("variant", {"type": "string", "enum": ["neutral", "info", "success", "warning", "error"]}),
        ),
    ),
    Component(
        "Table",
        "ax",
        "Table",
        "A table of row objects; columns lists the keys to show",
        (Prop("rows", {"type": "array", "items": {"type": "object"}}, True), Prop("columns", _STRINGS)),
    ),
    Component(
        "CodeBlock",
        "ax",
        "CodeBlock",
        "Highlighted source code",
        (Prop("code", _STRING, True), Prop("language", _STRING)),
    ),
    Component(
        "Plot",
        "go",
        "FigureWidget",
        "An empty Plotly figure that the callbacks fill, such as self.ui.chart.add_traces(...); "
        "layout holds literal Plotly layout keys, such as {height: 320}",
        (Prop("layout", {"type": "object"}),),
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
_ANNOTATIONS = {
    "bool": _BOOLEAN,
    "int": _NUMBER,
    "float": _NUMBER,
    "str": _STRING,
    "Iterable[str]": _STRINGS,
    "Iterable[int]": _NUMBERS,
    "Iterable[Mapping[str, Any]]": {"type": "array", "items": {"type": "object"}},
    "Iterable[Any]": {"type": "array"},
    "Mapping[str, Any]": {"type": "object"},
    "Mapping[str, str]": {"type": "object"},
    "TitleInput": {"anyOf": [_STRINGS, {"type": "object"}]},
}


def _with_options(component: Component) -> Component:
    if not component.module:
        return component

    cls = getattr(_MODULES[component.module], component.cls)
    taken = {prop.keyword for prop in component.props} | {key for key, _ in component.fixed}
    doc = inspect.cleandoc(cls.__doc__ or "")
    parameters = _parameters(doc)
    literals = _astryx_literals(doc)
    renamed = _astryx_names(cls)
    properties = {}
    for name, parameter in inspect.signature(cls.__init__).parameters.items():
        if name == "self" or name in taken or parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            continue

        schema = _annotation_schema(str(parameter.annotation))
        if schema is None:
            continue

        kind, description = parameters.get(name, ("", ""))
        values = _set_literals(kind) or literals.get(renamed.get(name, _camel(name)), [])
        if schema == _STRING and values:
            default = parameter.default
            extra = [default] if isinstance(default, str) and default not in values else []
            schema = {"type": "string", "enum": [*values, *extra]}

        properties[name] = {**schema, "description": description}

    if not properties:
        return component

    schema = {"type": "object", "properties": properties, "additionalProperties": False}

    return replace(component, props=(*component.props, Prop("options", schema, kind=PropKind.OPTIONS)))


# Callables and other Python-only types have no OpenUI literal, so their keywords stay out of options.
def _annotation_schema(annotation: str) -> dict[str, Any] | None:
    schemas = []
    for part in (part.strip() for part in annotation.split(" | ")):
        if part == "None":
            continue

        if part not in _ANNOTATIONS:
            return None

        if _ANNOTATIONS[part] not in schemas:
            schemas.append(_ANNOTATIONS[part])

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


# A numpydoc type such as ``{'top', 'left'}, default 'top'`` lists the values the wrapper accepts.
def _set_literals(kind: str) -> list[str]:
    match = re.match(r"^\{([^}]*)\}", kind)

    return re.findall(r"['\"]([^'\"]*)['\"]", match.group(1)) if match else []


# The ``Astryx Props`` section lists string unions such as ``('compact' or 'balanced')`` by Astryx prop
# name, with entries wrapped onto indented lines. They apply to keywords the wrapper passes through.
def _astryx_literals(doc: str) -> dict[str, list[str]]:
    entries = re.sub(r"\n  +", " ", doc)
    matches = re.finditer(r"^- ``(\w+)`` \(((?:'[^']*'(?: or )?)+)(?:;[^)]*)?\)", entries, re.M)

    return {match.group(1): re.findall(r"'([^']*)'", match.group(2)) for match in matches}


# Wrappers pass keywords on as ``astryxName=keyword``; the source gives the names that differ.
def _astryx_names(cls: type) -> dict[str, str]:
    source = inspect.getsource(cls.__init__)

    return {keyword: prop for prop, keyword in re.findall(r"\b(\w+)=(\w+)[,)\s]", source) if prop != keyword}


def _camel(name: str) -> str:
    head, *rest = name.split("_")

    return head + "".join(part.capitalize() for part in rest)


COMPONENTS: tuple[Component, ...] = tuple(
    _with_options(component) for component in _COMPONENTS if _MODULES.get(component.module, al) is not None
)
CATALOG: dict[str, Component] = {component.name: component for component in COMPONENTS}

_CALLBACK_PARAMS = {
    "type": "object",
    "properties": {"handler": _STRING, "context": {}},
    "required": ["handler"],
}
_CALLBACK_DESCRIPTION = "Calls the Python callback named handler with the event and the widgets"


def library_spec() -> dict[str, Any]:
    """Return the OpenUI LibrarySpec for the catalog, with the `Callback` custom action."""
    defs: dict[str, Any] = {component.name: _component_schema(component) for component in COMPONENTS}
    defs["Component"] = {"anyOf": [{"$ref": f"#/$defs/{component.name}"} for component in COMPONENTS]}
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
            "properties": {component.name: {"$ref": f"#/$defs/{component.name}"} for component in COMPONENTS},
            "$defs": defs,
            "actions": {CALLBACK: {"description": _CALLBACK_DESCRIPTION, "params": _CALLBACK_PARAMS}},
        },
        "components": {
            component.name: {"signature": _signature(component), "description": component.description}
            for component in COMPONENTS
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
