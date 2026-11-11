"""Agreement between the Python widget classes and the Astryx frontend code.

The kernel and the browser share trait names, component names, and message
types only as strings, so nothing else notices when one side renames or drops
one. These tests read the frontend sources as text and compare them with the
Python classes.
"""

from __future__ import annotations

import ast
import enum
import inspect
import re
import sys
import typing
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import anywidget
import pytest

import anylumino as al
import anylumino.astryx as ax
from anylumino.astryx.base import _ASTRYX_COMPONENT_NAMES
from anylumino.astryx.base import Widget
from anylumino.components import ComponentWidget


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "anylumino" / "static" / "astryx"
FRONTEND_SOURCES = sorted([*STATIC.glob("*.mjs"), STATIC / "astryx_widget.js", *(STATIC / "components").glob("*.mjs")])
PYTHON_SOURCES = [*(ROOT / "src" / "anylumino" / "astryx").glob("*.py"), ROOT / "src" / "anylumino" / "components.py"]

sys.path.insert(0, str(ROOT / "scripts"))
import docs_examples  # noqa: E402

# Attributes that a wrapper keyword can set as a trait, with a value no default uses.
SHARED_VALUES = {"label": "contract-label", "disabled": True, "icon": "contract-icon"}




def frontend_text() -> str:
    return "\n".join(path.read_text() for path in FRONTEND_SOURCES)


def widget_classes() -> list[type[Widget]]:
    found: set[type[Widget]] = set()

    def walk(cls: type) -> None:
        for subclass in cls.__subclasses__():
            # anywidget gives every instance a subclass of its own under the same
            # name, so only the class its module defines counts.
            module = sys.modules.get(subclass.__module__)
            if subclass.__module__.startswith("anylumino.") and getattr(module, subclass.__qualname__, None) is subclass:
                found.add(subclass)
                walk(subclass)

    walk(Widget)

    return sorted(found, key=lambda cls: cls.__name__)


def component_name(cls: type[Widget]) -> str | None:
    match = re.search(r'super\(\).__init__\(\s*"(\w+)"', inspect.getsource(cls.__init__))

    return match.group(1) if match else None


def synced_traits() -> dict[str, set[str]]:
    base = set(anywidget.AnyWidget().keys)
    traits: dict[str, set[str]] = {}
    for cls in [ComponentWidget, *widget_classes()]:
        for name in cls.class_traits(sync=True):
            if name not in base:
                traits.setdefault(name, set()).add(cls.__name__)

    return traits


def frontend_trait_reads(text: str) -> set[str]:
    return set(re.findall(r'model\.get\("(\w+)"\)', text)) | set(re.findall(r'model\.set\("(\w+)"', text))


def test_frontend_reads_traits_with_literal_names() -> None:
    # The other checks find trait reads by this one shape, so any other shape would hide a read.
    assert re.findall(r'model\.get\((?!")[^)]*\)', frontend_text()) == []


def test_every_synced_trait_is_read_by_the_frontend() -> None:
    unread = {name for name in synced_traits() if name not in frontend_trait_reads(frontend_text())}

    assert sorted(unread) == []


def test_frontend_reads_only_synced_traits() -> None:
    base = set(anywidget.AnyWidget().keys)

    assert frontend_trait_reads(frontend_text()) - set(synced_traits()) - base == set()


def spec_entries(text: str) -> dict[str, str]:
    """Return the text of every component spec, by component name."""
    entries: dict[str, str] = {}
    for table in re.finditer(r"^export const SPECS = \{\n(.*?)^\};", text, re.M | re.S):
        for entry in re.finditer(r"^  (\w+): \{(?: [^\n]* \},|\n.*?^  \},)$", table.group(1), re.M | re.S):
            entries[entry.group(1)] = entry.group(0)

    return entries


def registered_names(text: str) -> set[str]:
    return set(spec_entries(text))


def test_every_python_component_name_is_registered_in_the_frontend() -> None:
    python_names = {name for cls in widget_classes() if (name := component_name(cls))} | _ASTRYX_COMPONENT_NAMES

    assert python_names - registered_names(frontend_text()) == set()


def python_message_handlers(text: str) -> set[str]:
    return set(re.findall(r'(?:msg_type|content\.get\("type"\))\s*[!=]=\s*"([\w-]+)"', text))


def test_every_message_the_frontend_sends_has_a_python_handler() -> None:
    text = frontend_text()
    sent = set(re.findall(r'(?:model\.send|sendModelAction)\(\{\s*type: "([\w-]+)"', text))
    sent |= {"click"} if "sendModelAction(" in text else set()
    python = "\n".join(path.read_text() for path in PYTHON_SOURCES)

    assert sent
    assert sent - python_message_handlers(python) == set()


def test_every_message_python_sends_has_a_frontend_handler() -> None:
    python = "\n".join(path.read_text() for path in PYTHON_SOURCES)
    sent = set(re.findall(r'self\.send\(\s*\{\s*"type":\s*"([\w-]+)"', python))
    handled = set(re.findall(r'content\?\.type\s*[!=]==\s*"([\w-]+)"', frontend_text()))

    assert sent
    assert sent - handled == set()


def component_examples() -> Iterator[tuple[type[Widget], ast.Call, dict[str, Any]]]:
    """Yield each widget class with the outermost call that builds it in its docstring example."""
    classes = {cls.__name__: cls for cls in widget_classes()}
    for _slug, path, code in docs_examples.component_examples():
        cls = classes.get(path.removeprefix("ax."))
        if not path.startswith("ax.") or cls is None:
            continue

        namespace: dict[str, Any] = {"al": al, "ax": ax}
        exec(compile(code, "example", "exec"), namespace)
        calls = [
            node
            for node in ast.walk(ast.parse(code))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == cls.__name__
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "ax"
        ]
        if calls:
            yield cls, calls[0], namespace


def variant_value(cls: type[Widget]) -> Any:
    hint = typing.get_type_hints(cls.__init__).get("variant")
    for option in typing.get_args(hint) or (hint,):
        if isinstance(option, type) and issubclass(option, enum.Enum):
            return list(option)[-1].value

    return "contract-variant"


def build_with_shared_values(cls: type[Widget], call: ast.Call, namespace: dict[str, Any]) -> tuple[Widget, dict[str, Any]]:
    args = [eval(compile(ast.Expression(arg), "example", "eval"), namespace) for arg in call.args]
    kwargs = {
        keyword.arg: eval(compile(ast.Expression(keyword.value), "example", "eval"), namespace)
        for keyword in call.keywords
        if keyword.arg
    }
    signature = inspect.signature(cls.__init__)
    bound = signature.bind_partial(None, *args, **kwargs)
    values = {**SHARED_VALUES, "variant": variant_value(cls)}
    given = {name: value for name, value in values.items() if name in signature.parameters}
    bound.arguments.update(given)

    return cls(*bound.args[1:], **bound.kwargs), given


def prop_holds(props: Any, name: str, value: Any) -> bool:
    keys = {"disabled": ("isDisabled", "disabled")}.get(name, (name,))
    if isinstance(props, Mapping):
        return any(key in keys and item == value for key, item in props.items()) or any(
            prop_holds(item, name, value) for item in props.values()
        )

    return False


def function_body(text: str, name: str) -> str:
    match = re.search(r"^(?:export )?function %s\(.*?^\}\n" % name, text, re.M | re.S)

    return match.group(0) if match else ""


def frontend_block(text: str, name: str) -> str:
    """Return the frontend code that renders component ``name``.

    That is its spec, the functions the spec names or calls, and the default
    children function when the spec has none, followed two calls deep.
    """
    entry = spec_entries(text).get(name, "")
    parts = [entry]
    if "children:" not in entry and "view:" not in entry:
        parts.append(function_body(text, "slotsOrText"))
    for _depth in range(2):
        called = set(re.findall(r"(?:view|props|children): (\w+)\b(?!\s*\()", "\n".join(parts)))
        called |= set(re.findall(r"(?<![\w.])(\w+)\(", "\n".join(parts)))
        parts += [body for function in sorted(called) if (body := function_body(text, function)) not in parts]

    return "\n".join(parts)


def reads_shared_value(block: str, name: str) -> bool:
    local = r'(?<![\w.?"\'])%s(?!\s*:)\b' % name
    forwarded = any(name in re.findall(r'"(\w+)"', listing) for listing in re.findall(r"traits: \[([^\]]*)\]", block))

    return bool(forwarded or re.search(local, block) or re.search(r'model\.get\("%s"\)' % name, block))


def attribute_gaps() -> set[tuple[str, str, str]]:
    text = frontend_text()
    gaps: set[tuple[str, str, str]] = set()
    for cls, call, namespace in component_examples():
        widget, given = build_with_shared_values(cls, call, namespace)
        block = frontend_block(text, widget.component_name)
        for name, value in given.items():
            in_trait = getattr(widget, name) == value
            in_props = prop_holds(widget.props, name, value)
            if in_trait and in_props:
                gaps.add((cls.__name__, name, "trait and props"))
            elif in_trait and not reads_shared_value(block, name):
                gaps.add((cls.__name__, name, "trait unread"))
            elif in_props:
                gaps.add((cls.__name__, name, "props only"))

    return gaps


def test_shared_attributes_have_one_home_that_the_frontend_reads() -> None:
    assert sorted(attribute_gaps()) == []


def test_every_widget_class_has_a_docstring_example() -> None:
    # The shared attribute check builds each class from its example.
    covered = {cls for cls, _call, _namespace in component_examples()}
    concrete = {cls for cls in widget_classes() if component_name(cls)}

    assert sorted(cls.__name__ for cls in concrete - covered) == []


@pytest.fixture(autouse=True)
def repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    # The example collector reads paths relative to the repository root.
    monkeypatch.chdir(ROOT)
