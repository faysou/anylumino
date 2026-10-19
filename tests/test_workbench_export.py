import os
import sys
from pathlib import Path

import IPython
import pandas as pd
import pytest

import anylumino as al
from anylumino.workbench import Workbench, load
from anylumino.workbench.export import module_source
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
    dialog.export()

    assert dialog.is_open is False
    assert (project / "exports" / "explorer.py").read_text() == module_source(code(built)["ui_code"], CALLBACKS)
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
    built.export(tmp_path, "sales")
    assert built.chat.messages[-1]["content"].startswith(
        f"Exported `{tmp_path / 'sales.py'}`."
    )


def test_export_failure_is_reported(built, tmp_path):
    built.export(tmp_path / "missing", "sales")
    assert built.chat.messages[-1]["content"].startswith("Export failed: [Errno 2] No such file or directory")


def test_export_is_disabled_until_a_ui_is_built(tmp_path):
    assert Workbench(agent="codex", cwd=tmp_path).export_button.disabled is True


def test_load_builds_the_ui_with_the_namespace_keywords(built, tmp_path):
    built.export(tmp_path, "sales")
    sales = pd.DataFrame({"region": ["AMER"], "revenue": [4.0]})

    ui = load(str(tmp_path / "sales.py"), sales=sales)
    click(ui.go)

    assert (type(ui).__name__, type(ui.app).__name__, ui.app.sales, ui.app.ui) == ("UI", "SalesApp", sales, ui)
    assert ui.widgets == [ui.root]
    assert ui.title.text == "Total 4.0"
    assert [(row["region"], row["revenue"]) for row in ui.table.rows] == [("AMER", 4.0)]
    with pytest.warns(UserWarning, match="No workbench is attached, so ask_agent ignored 'Summarize'."):
        click(ui.ask)


def test_load_reads_no_notebook_globals(built, tmp_path, monkeypatch):
    built.export(tmp_path, "sales")
    monkeypatch.setattr(sys.modules["__main__"], "sales", SALES, raising=False)

    with pytest.raises(AttributeError, match="'SalesApp' object has no attribute 'sales'"):
        load(tmp_path / "sales.py")


def test_exported_file_works_as_an_imported_module(built, tmp_path, monkeypatch):
    built.export(tmp_path, "sales")
    monkeypatch.syspath_prepend(str(tmp_path))
    from sales import UI, SalesApp

    ui = UI(SalesApp(sales=SALES))
    click(ui.go)

    assert ui.title.text == "Total 1.0"
    assert [(row["region"], row["revenue"]) for row in ui.table.rows] == [("EMEA", 1.0)]


def test_app_is_composable_in_another_layout(built, tmp_path):
    built.export(tmp_path, "sales")
    first = load(tmp_path / "sales.py", sales=SALES)
    second = load(tmp_path / "sales.py", sales=SALES)

    tabs = al.TabPanel([first, second], titles=["First", "Second"])
    click(second.go)

    assert tabs.widgets == [first, second]
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
    built.export(tmp_path, "sales")
    relative = Path(os.path.relpath(tmp_path, Path(__file__).parent))

    root = load(relative / "sales.py", sales=SALES)

    assert root.title.text == "Sales"


def test_load_resolves_relative_paths_against_the_notebook_directory(built, tmp_path, monkeypatch):
    built.export(tmp_path, "sales")

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
