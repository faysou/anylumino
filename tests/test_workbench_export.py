import os
import re
import sys
from pathlib import Path

import IPython
import pandas as pd
import pytest

import anylumino as al
from anylumino.workbench import Workbench, load
from anylumino.workbench.export import ExportedFileError, class_source, module_source, read_module, ui_fingerprint
from test_workbench import click, code, reply


PROGRAM = """root = VBox([title, go, ask, table])
title = Heading("Sales")
go = Button("Total", @Callback("on_total"))
ask = Button("Ask", @Callback("on_ask"))
table = Table([], ["region", "revenue"])"""

CALLBACKS = """from anylumino.workbench import App


class SalesApp(App):
    def setup(self):
        self.ui.table.set_rows(self.sales.to_dict("records"))

    def on_total(self, event):
        self.ui.title.text = f"Total {self.sales['revenue'].sum()}"

    def on_ask(self, event):
        self.ask_agent("Summarize")
"""

SALES = pd.DataFrame({"region": ["EMEA"], "revenue": [1.0]})


@pytest.fixture
def built(agent_reply, tmp_path, monkeypatch):
    project = tmp_path / "project"
    (project / "exports" / "old").mkdir(parents=True)
    (project / ".hidden").mkdir()
    monkeypatch.chdir(project)
    agent_reply(reply("Done.", PROGRAM, CALLBACKS))
    sales = pd.DataFrame({"region": ["EMEA", "APAC"], "revenue": [1.5, 2.0]})
    workbench = Workbench(agent="codex", session="sales", namespace={"sales": sales}, cwd=tmp_path)
    workbench.submit("Build it")

    return workbench


def labels(widgets):
    return [widget.label for widget in widgets]


def test_export_writes_the_tabs_and_posts_the_load_call(built, tmp_path):
    dialog = built.export_dialog
    assert built.export_button.disabled is False

    click(built.export_button)
    project = tmp_path / "project"
    assert (dialog.is_open, dialog.path.text, labels(dialog.folders.widgets)) == (True, str(project), ["exports/"])
    assert (dialog.name.value, dialog.files.text) == (
        "sales",
        "Writes sales.py here, replacing an existing file.",
    )
    click(dialog.folders.widgets[0])
    assert (dialog.path.text, labels(dialog.folders.widgets)) == (str(project / "exports"), ["old/"])
    dialog.name.value = "explorer"
    assert dialog.files.text == "Writes explorer.py here, replacing an existing file."
    (project / "exports" / "explorer.py").write_text("old")
    dialog.finish()

    assert dialog.is_open is False
    assert (project / "exports" / "explorer.py").read_text() == module_source(
        code(built)["ui_code"], CALLBACKS, PROGRAM
    )
    assert built.chat.messages[-1] == {
        "role": "assistant",
        "content": "Exported `exports/explorer.py`. Show the same UI in a notebook cell with:\n\n"
        '```python\nfrom anylumino.workbench import load\n\nload("exports/explorer.py", sales=sales)\n```',
    }


def test_export_dialog_goes_up_and_keeps_the_last_folder(built, tmp_path):
    dialog = built.export_dialog
    click(built.export_button)
    up = dialog.widgets[0].widgets[1].widgets[1]
    click(up)
    assert dialog.path.text == str(tmp_path)
    dialog.hide()

    click(built.export_button)
    assert (dialog.is_open, dialog.path.text) == (True, str(tmp_path))


def test_export_outside_the_current_directory_shows_absolute_paths(built, tmp_path):
    built.export(tmp_path / "sales.py")
    assert built.chat.messages[-1]["content"].startswith(
        f"Exported `{tmp_path / 'sales.py'}`."
    )


def test_export_failure_is_reported(built, tmp_path):
    built.export(tmp_path / "missing" / "sales.py")
    assert built.chat.messages[-1]["content"].startswith("Export failed: [Errno 2] No such file or directory")


def test_export_from_a_cell_writes_a_relative_path_and_import_reads_it_back(built, tmp_path):
    # The built fixture runs in tmp_path / "project", so the relative path lands there
    built.export("exports/sales.py")

    workbench = Workbench(agent="codex", namespace={"sales": SALES}, cwd=tmp_path)
    workbench.import_file("exports/sales.py")

    assert (tmp_path / "project" / "exports" / "sales.py").is_file()
    assert built.chat.messages[-1]["content"].startswith("Exported `exports/sales.py`.")
    assert code(workbench) == code(built)
    assert workbench.chat.messages == [{"role": "system", "content": "Imported `exports/sales.py`."}]


def test_export_without_a_ui_writes_nothing(tmp_path):
    workbench = Workbench(agent="codex", cwd=tmp_path)

    workbench.export(tmp_path / "sales.py")

    assert (tmp_path / "sales.py").exists() is False
    assert workbench.chat.messages == [{"role": "system", "content": "Export failed: there is no UI yet."}]


def test_export_is_disabled_until_a_ui_is_built(tmp_path):
    assert Workbench(agent="codex", cwd=tmp_path).export_button.disabled is True


def test_load_builds_the_ui_with_the_namespace_keywords(built, tmp_path):
    built.export(tmp_path / "sales.py")
    sales = pd.DataFrame({"region": ["AMER"], "revenue": [4.0]})

    ui = load(str(tmp_path / "sales.py"), sales=sales)
    click(ui.go)

    assert (type(ui).__name__, type(ui.app).__name__, ui.app.sales, ui.app.ui) == ("UI", "SalesApp", sales, ui)
    assert ui.widget is ui.root
    assert ui.title.text == "Total 4.0"
    assert [(row["region"], row["revenue"]) for row in ui.table.rows] == [("AMER", 4.0)]
    with pytest.warns(UserWarning, match="No workbench is attached, so ask_agent ignored 'Summarize'."):
        click(ui.ask)


def test_load_reads_no_notebook_globals(built, tmp_path, monkeypatch):
    built.export(tmp_path / "sales.py")
    monkeypatch.setattr(sys.modules["__main__"], "sales", SALES, raising=False)

    with pytest.raises(AttributeError, match="'SalesApp' object has no attribute 'sales'"):
        load(tmp_path / "sales.py")


def test_exported_file_works_as_an_imported_module(built, tmp_path, monkeypatch):
    built.export(tmp_path / "sales.py")
    monkeypatch.syspath_prepend(str(tmp_path))
    from sales import UI, SalesApp

    ui = UI(SalesApp(sales=SALES))
    click(ui.go)

    assert ui.title.text == "Total 1.0"
    assert [(row["region"], row["revenue"]) for row in ui.table.rows] == [("EMEA", 1.0)]


def test_app_is_composable_in_another_layout(built, tmp_path):
    built.export(tmp_path / "sales.py")
    first = load(tmp_path / "sales.py", sales=SALES)
    second = load(tmp_path / "sales.py", sales=SALES)

    tabs = al.TabPanel([first, second], titles=["First", "Second"])
    click(second.go)

    assert (tabs.widgets, tabs.get_owner(tabs.child_keys[0])) == ([first.widget, second.widget], first)
    assert (first.title.text, second.title.text) == ("Sales", "Total 1.0")


def test_module_source_puts_the_ui_first_and_moves_the_callbacks_imports_up():
    ui_code = '''"""Generated."""

import anylumino.astryx as ax


class UI(ax.Stack):
    pass
'''
    callbacks = '''import math
from anylumino.workbench import App


class SalesApp(App):
    pass
'''
    assert module_source(ui_code, callbacks) == '''"""Generated."""

import anylumino.astryx as ax
import math
from anylumino.workbench import App


class UI(ax.Stack):
    pass


class SalesApp(App):
    pass
'''


def test_module_source_puts_future_imports_first():
    ui_code = '''"""Generated."""

import anylumino.astryx as ax


class UI(ax.Stack):
    pass
'''
    callbacks = '''"""Callbacks."""

from __future__ import annotations

from anylumino.workbench import App


class SalesApp(App):
    pass
'''
    assert module_source(ui_code, callbacks) == '''"""Generated."""
from __future__ import annotations

import anylumino.astryx as ax
"""Callbacks."""
from anylumino.workbench import App


class UI(ax.Stack):
    pass


class SalesApp(App):
    pass
'''


def test_module_source_drops_imports_the_ui_code_already_has():
    ui_code = '''import anylumino.astryx as ax
import plotly.graph_objects as go
from anylumino.workbench import Event, View


class UI(ax.Stack):
    pass
'''
    callbacks = '''import plotly.graph_objects as go
from anylumino.workbench import App, Event
from anylumino.workbench import View
from anylumino.workbench import View as Base


class ChartApp(App):
    pass
'''
    assert module_source(ui_code, callbacks) == '''import anylumino.astryx as ax
import plotly.graph_objects as go
from anylumino.workbench import Event, View
from anylumino.workbench import App
from anylumino.workbench import View as Base


class UI(ax.Stack):
    pass


class ChartApp(App):
    pass
'''


def test_export_name_defaults_to_an_importable_session_name(agent_reply, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    agent_reply(reply("Done.", PROGRAM, CALLBACKS))
    workbench = Workbench(agent="codex", session="sales-q3", namespace={"sales": SALES}, cwd=tmp_path)
    workbench.submit("Build it")
    click(workbench.export_button)
    assert workbench.export_dialog.name.value == "sales_q3"


def test_export_dialog_opens_in_the_directory_current_at_first_open(built, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path / "project" / "exports")
    click(built.export_button)
    assert built.export_dialog.path.text == str(tmp_path / "project" / "exports")


def test_load_resolves_relative_paths_against_the_calling_script(built, tmp_path):
    built.export(tmp_path / "sales.py")
    relative = Path(os.path.relpath(tmp_path, Path(__file__).parent))

    root = load(relative / "sales.py", sales=SALES)

    assert root.title.text == "Sales"


def test_load_resolves_relative_paths_against_the_notebook_directory(built, tmp_path, monkeypatch):
    built.export(tmp_path / "sales.py")

    class ZMQInteractiveShell:
        pass

    monkeypatch.setattr(IPython, "get_ipython", ZMQInteractiveShell)
    monkeypatch.chdir(tmp_path)

    root = load("sales.py", sales=SALES)

    assert root.title.text == "Sales"


def test_export_dialog_width_does_not_size_its_host(tmp_path):
    # A host width would keep header space while the dialog is closed
    dialog = Workbench(agent="codex", cwd=tmp_path).export_dialog
    assert (dialog.width, dialog.props["width"], dialog.props["isInline"]) == ("", 480, False)


def test_export_writes_the_program_as_a_comment_that_reads_back(built, tmp_path):
    built.export(tmp_path / "sales.py")
    source = (tmp_path / "sales.py").read_text()

    exported = read_module(source)

    fingerprint = ui_fingerprint(class_source(code(built)["ui_code"], "UI"))
    assert source.startswith(
        '"""Generated by the anylumino workbench from an OpenUI program."""\n\n'
        f"# ```openui-lang ui-sha256={fingerprint}\n# root = VBox([title, go, ask, table])\n# title = Heading(\"Sales\")\n"
    )
    assert (exported.program, exported.callbacks, exported.ui_edited) == (PROGRAM, CALLBACKS, False)
    assert exported.ui_class == class_source(code(built)["ui_code"], "UI")
    assert len(fingerprint) == 16


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("class UI:\n    pass\n", "the file has no OpenUI program between '# ```openui-lang' and '# ```' lines"),
        ("# ```openui-lang\n# root = VBox([])\n# ```\nx = 1\n", "the file has no UI class"),
    ],
    ids=["no-program", "no-ui-class"],
)
def test_read_module_rejects_files_that_are_not_exports(source, message):
    with pytest.raises(ExportedFileError, match=f"^{re.escape(message)}$"):
        read_module(source)


def imported(agent_reply, tmp_path, source):
    path = tmp_path / "edited.py"
    path.write_text(source)
    workbench = Workbench(agent="codex", namespace={"sales": SALES}, cwd=tmp_path)
    log = tmp_path / "log.jsonl"
    calls = len(agent_reply.calls()) if log.exists() else 0
    workbench.import_file(path)

    return workbench, agent_reply.calls()[calls:] if log.exists() else []


def test_import_of_an_unchanged_export_fills_the_tabs_without_the_agent(built, agent_reply, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    built.export(tmp_path / "edited.py")

    workbench, calls = imported(agent_reply, tmp_path, (tmp_path / "edited.py").read_text())

    assert calls == []
    assert code(workbench) == code(built)
    assert workbench.chat.messages == [{"role": "system", "content": "Imported `edited.py`."}]
    assert (workbench.running, workbench.export_button.disabled) == (False, False)


def test_import_regenerates_the_ui_from_an_edited_program_comment(built, agent_reply, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    built.export(tmp_path / "edited.py")
    source = (tmp_path / "edited.py").read_text().replace('# title = Heading("Sales")', '# title = Heading("Revenue")')

    workbench, calls = imported(agent_reply, tmp_path, source)

    assert calls == []
    assert code(workbench)["openui"] == PROGRAM.replace('Heading("Sales")', 'Heading("Revenue")')
    assert "self.title = ax.Heading(text='Revenue')" in code(workbench)["ui_code"]
    assert workbench.chat.messages == [{"role": "system", "content": "Imported `edited.py`."}]


def test_import_keeps_callbacks_edited_outside(built, agent_reply, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    built.export(tmp_path / "edited.py")
    source = (tmp_path / "edited.py").read_text().replace('f"Total {', 'f"Sum {')

    workbench, calls = imported(agent_reply, tmp_path, source)
    click(workbench.ui.go)

    assert calls == []
    assert code(workbench)["callbacks"] == CALLBACKS.replace('f"Total {', 'f"Sum {')
    assert workbench.ui.title.text == "Sum 1.0"


@pytest.mark.parametrize(
    ("edit", "reason", "report"),
    [
        (
            ("self.title = ax.Heading(text='Sales')", "self.title = ax.Heading(text='Revenue')"),
            "its UI class was edited, so it differs from the code its program generates",
            ["Reconciled `edited.py`: the generated UI class matches the file."],
        ),
        (
            ("    def on_total(self, event):", "    def on_total(self, event)"),
            "it is not valid Python: expected ':' (line {line})",
            [],
        ),
    ],
    ids=["edited-ui-class", "invalid-python"],
)
def test_import_asks_the_agent_to_reconcile_a_changed_file(
    built, agent_reply, tmp_path, monkeypatch, edit, reason, report
):
    monkeypatch.chdir(tmp_path)
    built.export(tmp_path / "edited.py")
    source = (tmp_path / "edited.py").read_text().replace(*edit)
    if "{line}" in reason:
        reason = reason.format(line=source.splitlines().index("    def on_total(self, event)") + 1)

    agent_reply(reply("Reconciled.", PROGRAM.replace('Heading("Sales")', 'Heading("Revenue")'), CALLBACKS))

    workbench, calls = imported(agent_reply, tmp_path, source)

    (call,) = calls
    assert call["stdin"].startswith(
        f"Reconcile the imported file `edited.py`: {reason}.\n\n"
        f"The file `edited.py` was exported from this workbench and changed outside it, and {reason}. "
    )
    assert f"```text\n{source}\n```" in call["stdin"]
    assert [message["content"] for message in workbench.chat.messages] == [
        f"Reconcile the imported file `edited.py`: {reason}.",
        "Reconciled.",
        *report,
    ]
    assert workbench.ui.title.text == "Revenue"
    assert workbench.running is False


def test_reconcile_that_misses_the_edit_is_reported(built, agent_reply, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    built.export(tmp_path / "edited.py")
    source = (tmp_path / "edited.py").read_text().replace("ax.Heading(text='Sales')", "ax.Heading(text='Revenue')")
    agent_reply(reply("Reconciled.", PROGRAM, CALLBACKS))

    workbench, calls = imported(agent_reply, tmp_path, source)

    assert len(calls) == 1
    assert workbench.chat.messages[-1] == {
        "role": "system",
        "content": "The generated UI class still differs from `edited.py`. The UI code tab shows what applied; "
        "ask the agent in the chat to close the gap.",
    }
    assert workbench.ui.title.text == "Sales"


def test_import_of_a_file_that_is_not_an_export_is_reported(agent_reply, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    workbench, calls = imported(agent_reply, tmp_path, "x = 1\n")

    assert calls == []
    assert workbench.chat.messages == [
        {
            "role": "system",
            "content": "Import of `edited.py` failed: "
            "the file has no OpenUI program between '# ```openui-lang' and '# ```' lines",
        }
    ]
    assert workbench.running is False


def test_import_dialog_lists_python_files_and_enables_import_on_pick(tmp_path, monkeypatch):
    (tmp_path / "exports").mkdir()
    (tmp_path / "sales.py").write_text("")
    (tmp_path / "notes.txt").write_text("")
    monkeypatch.chdir(tmp_path)
    picked = []
    workbench = Workbench(agent="codex", cwd=tmp_path)
    workbench.import_dialog.on_import = picked.append
    dialog = workbench.import_dialog

    click(workbench.import_button)
    before = (dialog.is_open, labels(dialog.folders.widgets), dialog.confirm.disabled, dialog.files.text)
    click(dialog.folders.widgets[1])
    after = (dialog.confirm.disabled, dialog.files.text)
    click(dialog.confirm)

    assert before == (True, ["exports/", "sales.py"], True, "Pick an exported file.")
    assert after == (False, "Imports sales.py into the workbench, replacing the current UI.")
    assert (picked, dialog.is_open) == ([tmp_path / "sales.py"], False)


def test_ui_fingerprint_ignores_layout_comments_and_keyword_order():
    first = "class UI:\n    def __init__(self):\n        self.a = f(x=1, y=2)\n"
    same = "class UI:\n    # Built by hand\n    def __init__(self):\n        self.a = f(y=2,  x=1)\n"
    other = "class UI:\n    def __init__(self):\n        self.a = f(x=1, y=3)\n"

    assert ui_fingerprint(first) == ui_fingerprint(same)
    assert ui_fingerprint(first) != ui_fingerprint(other)
