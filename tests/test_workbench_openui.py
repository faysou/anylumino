import asyncio

import pandas as pd
import pytest

import anylumino as al
from anylumino import astryx as ax
from anylumino.workbench import codegen, openui, prompt, skill
from anylumino.workbench.catalog import CATALOG, COMPONENTS, PropKind, go, library_spec, type_name


SAMPLES = {"string": "s", "number": 2, "boolean": True, "object": {"height": 300}}


def sample(prop):
    schema = prop.schema
    if prop.kind == PropKind.CHILDREN:
        return [ax.Text("first"), ax.Text("second")]

    if "enum" in schema:
        return schema["enum"][-1]

    if schema.get("type") == "array":
        item = schema.get("items", {}).get("type", "string")

        return [{"a": 1}] if item == "object" else [SAMPLES[item], SAMPLES[item]]

    return SAMPLES[schema["type"]]


def test_catalog_lists_components_and_props_in_order():
    assert {component.name: [prop.name for prop in component.props] for component in COMPONENTS} == {
        "VBox": ["children", "gap", "options"],
        "HBox": ["children", "gap", "options"],
        "SplitPanel": ["children", "orientation", "sizes", "options"],
        "TabPanel": ["children", "titles", "options"],
        "Card": ["children", "options"],
        "Heading": ["text", "level", "options"],
        "Text": ["text", "options"],
        "Markdown": ["text", "options"],
        "Button": ["label", "action", "variant", "options"],
        "TextInput": ["label", "value", "placeholder", "on_change", "options"],
        "TextArea": ["label", "value", "placeholder", "rows", "on_change", "options"],
        "NumberInput": ["label", "value", "min", "max", "step", "on_change", "options"],
        "Selector": ["items", "value", "label", "on_change", "options"],
        "Slider": ["label", "value", "min", "max", "step", "on_change", "options"],
        "Switch": ["label", "value", "on_change", "options"],
        "Checkbox": ["label", "value", "on_change", "options"],
        "Badge": ["label", "variant"],
        "Table": ["rows", "columns", "options"],
        "CodeBlock": ["code", "language", "options"],
        "AppShell": ["content", "top_nav", "side_nav", "banner", "options"],
        "Layout": ["content", "header", "start", "end", "footer", "options"],
        "SideNav": ["items", "value", "on_change", "options"],
        "TopNav": ["items", "value", "end", "on_change", "options"],
        "Stepper": ["items", "value", "on_change", "options"],
        "OverflowList": ["items", "action", "options"],
        "ComplexSelector": ["label", "content", "value", "options"],
        "RichTextEditor": ["label", "value", "on_change", "options"],
        "RichTextView": ["text"],
        "Timer": ["options"],
        "Toast": ["options"],
        "Indicator": ["value", "options"],
        "NavIcon": ["icon"],
        "Plot": ["layout"],
        "Widget": ["name"],
    }


@pytest.mark.parametrize("component", [c for c in COMPONENTS if c.name != "Widget"], ids=lambda c: c.name)
def test_catalog_entry_builds_its_class(component):
    module = {"al": al, "ax": ax, "go": go}[component.module]
    kwargs = {prop.keyword: sample(prop) for prop in component.props if prop.kind not in (PropKind.ACTION, PropKind.OPTIONS)}
    kwargs.update(component.fixed)
    widget = getattr(module, component.cls)(**kwargs)
    assert isinstance(widget, getattr(module, component.cls))


def test_library_spec_matches_catalog():
    spec = library_spec()
    assert list(spec["components"]) == list(CATALOG)
    assert list(spec["schema"]["properties"]) == list(CATALOG)
    for name, component in CATALOG.items():
        assert list(spec["schema"]["$defs"][name]["properties"]) == [prop.name for prop in component.props]

    assert spec["components"]["Button"] == {
        "signature": 'Button(label: string, action?: ActionExpression, variant?: "primary" | "secondary" | "ghost" | "destructive", options?: object)',
        "description": "A button that runs its action when clicked",
    }
    assert spec["actions"] == {
        "Callback": {
            "signature": "Callback(handler: string, context?: any)",
            "description": "Calls the Python callback named handler with the event and the widgets",
        }
    }


def test_tool_parses_a_catalog_program():
    program = 'root = VBox([title, go])\ntitle = Heading("Sales")\ngo = Button("Run", @Callback("on_run"))'
    result = asyncio.run(openui.parse(program))
    title, go = result["root"]["props"]["children"]
    assert (result["root"]["typeName"], result["root"]["statementId"]) == ("VBox", "root")
    assert (title["typeName"], title["statementId"], title["props"]) == ("Heading", "title", {"text": "Sales"})
    assert (go["typeName"], go["statementId"], go["props"]["label"]) == ("Button", "go", "Run")
    assert go["props"]["action"] == {
        "steps": [{"type": "custom_action", "name": "Callback", "params": {"handler": "on_run"}}]
    }
    assert result["errors"] == []
    assert result["statements"] == ["root", "title", "go"]


def test_tool_reports_unknown_component():
    result = asyncio.run(openui.parse('root = VBox([chart])\nchart = Chart([1, 2])'))
    assert [(error["code"], error["statementId"]) for error in result["errors"]] == [
        ("unknown-component", "chart")
    ]
    assert "Chart" in result["errors"][0]["message"]


def test_tool_merges_patch_by_statement_name():
    current = 'root = VBox([title, note])\ntitle = Heading("Sales")\nnote = Text("n")'
    merged = asyncio.run(openui.merge(current, 'title = Heading("Revenue")'))
    assert merged == 'root = VBox([title, note])\ntitle = Heading("Revenue")\nnote = Text("n")'


def test_tool_needs_node(monkeypatch):
    monkeypatch.setenv("PATH", "")
    with pytest.raises(openui.OpenUIError, match="needs `node` on PATH"):
        asyncio.run(openui.parse('root = Text("a")'))


def test_system_prompt_teaches_only_supported_features():
    text = asyncio.run(prompt.system_prompt({}))
    for component in COMPONENTS:
        assert f"{component.name}(" in text

    assert "@Callback" in text
    assert "```openui-lang" in text
    assert prompt.COMPONENT_OPTIONS in text
    assert prompt.CALLBACKS in text
    assert "sort_direction" not in text
    for unsupported in ("Query(", "Mutation(", "@Run", "@Set", "$binding"):
        assert unsupported not in text

    assert len(text) < 15_000


def test_table_options_come_from_its_keywords():
    assert {name: type_name(schema) for name, schema in CATALOG["Table"].options.items()} == {
        "row_key": "string",
        "selected": "any[]",
        "selects": '"" | "single" | "multiple"',
        "sortable": "boolean",
        "sort_key": "string",
        "sort_direction": '"" | "asc" | "desc"',
        "select_all_label": "string",
        "width": "number | string",
        "height": "number | string",
        "density": '"compact" | "balanced" | "spacious"',
        "dividers": '"rows" | "columns" | "grid" | "none"',
        "striped": "boolean",
        "hover": "boolean",
        "vertical_align": '"middle" | "top" | "bottom"',
        "text_overflow": '"wrap" | "truncate"',
    }
    assert CATALOG["Table"].options["sortable"]["description"] == "Whether table columns should be sortable by default."
    assert library_spec()["components"]["Table"]["signature"] == "Table(rows: object[], columns?: string[], options?: object)"


def test_button_options_leave_out_python_callbacks():
    assert list(CATALOG["Button"].options) == ["disabled", "size", "loading", "tooltip"]


def test_option_values_come_from_the_wrapper_docstring_first():
    assert CATALOG["TextInput"].options["label_position"]["enum"] == ["top", "left"]
    assert CATALOG["Switch"].options["label_position"]["enum"] == ["start", "end"]
    assert CATALOG["Table"].options["selects"]["enum"] == ["", "single", "multiple"]
    assert "enum" not in CATALOG["Table"].options["sort_key"]


@pytest.mark.parametrize(
    ("component", "option", "values"),
    [
        ("Heading", "display_type", ["display-1", "display-2", "display-3"]),
        ("VBox", "wrap", ["nowrap", "wrap", "wrap-reverse"]),
        ("Card", "variant", ["default", "muted", "blue", "cyan", "gray", "green", "orange", "pink", "purple", "red", "teal", "yellow"]),
    ],
    ids=["renamed-prop", "default-suffix", "wrapped-entry"],
)
def test_option_values_come_from_astryx_props(component, option, values):
    assert CATALOG[component].options[option]["enum"] == values


@pytest.mark.parametrize(
    ("options", "path"),
    [("{sortable: \"yes\"}", "/options/sortable"), ("{density: \"tight\"}", "/options/density")],
    ids=["type", "enum"],
)
def test_options_are_checked_by_the_parser(options, path):
    result = asyncio.run(openui.parse(f'root = VBox([t])\nt = Table([{{"a": 1}}], ["a"], {options})'))
    assert [(error["code"], error["path"]) for error in result["errors"]] == [("type-mismatch", path)]


def test_skill_files_match_the_catalog():
    on_disk = {
        str(path.relative_to(skill.PLUGIN)): path.read_text()
        for path in skill.PLUGIN.rglob("*")
        if path.is_file()
    }
    assert on_disk == skill.files()


def test_namespace_summary_describes_data_frames():
    frame = pd.DataFrame({"region": ["EMEA"], "revenue": [1.5]})
    assert prompt.namespace_summary({"sales": frame, "limit": 3}) == "\n".join(
        [
            "## Namespace",
            "",
            "The app gets these names as attributes, such as `self.<name>`; `Widget(name)` mounts the widgets among them:",
            "",
            "- `sales`: `pandas.DataFrame`, shape (1, 2), columns `region` (str), `revenue` (float64)",
            "- `limit`: `builtins.int`",
        ]
    )
    assert prompt.namespace_summary({}) == "## Namespace\n\nThe namespace is empty."


def test_prompt_names_the_reserved_statement_names():
    assert codegen.RESERVED == {"app", "widget"}
    assert "Statement names cannot be `app` or `widget`." in prompt.CALLBACKS

