import pytest

from anylumino import MarkdownEditor


@pytest.fixture
def files(tmp_path):
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    first.write_text("# First\n\n$x$", encoding="utf-8")
    second.write_text("# Second", encoding="utf-8")
    (tmp_path / "skip.txt").write_text("not markdown", encoding="utf-8")

    return first, second


def request_close(editor, key):
    editor.tabs._handle_frontend_message(editor.tabs, {"type": "close", "key": key}, [])


def path_labels(editor):
    return [item["label"] for item in editor.path.props["items"]]


def test_opening_files_adds_one_tab_each_and_reopening_selects(files):
    first, second = files
    editor = MarkdownEditor([first, second])
    editor.open(first)

    assert editor.tabs.child_keys == ["document-1", "document-2"]
    assert editor.tabs.titles == ["first.md", "second.md"]
    assert editor.tabs.tabs_closable is True
    assert editor.tabs.selected_key == "document-1"
    assert editor.documents["document-2"].pane.value == "# Second"
    assert editor.status.text == "Opened first.md"


def test_the_path_of_the_selected_file_shows_under_the_menu(files):
    first, second = files
    editor = MarkdownEditor([first, second])
    opened = path_labels(editor)
    editor.tabs.select_key("document-1")

    assert opened == [*second.parent.parts[1:], "second.md"]
    assert path_labels(editor) == [*first.parent.parts[1:], "first.md"]
    assert editor.path.props["items"][-1] == {"label": "first.md", "current": True}


def test_editing_marks_the_tab_without_writing_the_file(files):
    first, _second = files
    editor = MarkdownEditor([first])
    pane = editor.documents["document-1"].pane
    pane.value = "# Edited"
    edited = editor.tabs.titles
    pane.value = "# First\n\n$x$"

    assert edited == ["* first.md"]
    assert editor.tabs.titles == ["first.md"]
    assert first.read_text(encoding="utf-8") == "# First\n\n$x$"


def test_menu_save_writes_the_selected_tab_and_clears_the_mark(files):
    first, second = files
    editor = MarkdownEditor([first, second])
    editor.documents["document-2"].pane.value = "# Saved"
    editor.menu.callbacks["save"]("save")

    assert second.read_text(encoding="utf-8") == "# Saved"
    assert editor.tabs.titles == ["first.md", "second.md"]
    assert editor.status.text == "Saved second.md"


def test_save_as_writes_a_new_file_and_keeps_editing_it(files):
    first, _second = files
    editor = MarkdownEditor([first])
    editor.documents["document-1"].pane.value = "# Copy"
    editor.menu.callbacks["save_as"]("save_as")
    dialog = editor.save_as_dialog
    suggested = dialog.name.value
    dialog.name.value = "copy"
    dialog.finish()
    copy = first.parent / "copy.md"

    assert suggested == "first.md"
    assert copy.read_text(encoding="utf-8") == "# Copy"
    assert first.read_text(encoding="utf-8") == "# First\n\n$x$"
    assert editor.documents["document-1"].path == copy
    assert editor.tabs.titles == ["copy.md"]
    assert path_labels(editor)[-1] == "copy.md"


def test_closing_a_saved_tab_removes_it(files):
    first, second = files
    editor = MarkdownEditor([first, second])
    request_close(editor, "document-2")

    assert editor.tabs.child_keys == ["document-1"]
    assert list(editor.documents) == ["document-1"]
    assert editor.close_dialog.is_open is False
    assert editor.status.text == "Closed second.md"


def test_closing_an_unsaved_tab_asks_first(files):
    first, _second = files
    editor = MarkdownEditor([first])
    editor.documents["document-1"].pane.value = "# Unsaved"
    request_close(editor, "document-1")

    assert editor.tabs.child_keys == ["document-1"]
    assert editor.close_dialog.is_open is True
    assert editor.close_dialog.message.text == "first.md has unsaved changes. Close it anyway?"


@pytest.mark.parametrize(
    ("choice", "keys", "written"),
    [
        ("Cancel", ["document-1"], "# First\n\n$x$"),
        ("Discard changes", [], "# First\n\n$x$"),
        ("Save and close", [], "# Unsaved"),
    ],
)
def test_close_dialog_choices(files, choice, keys, written):
    first, _second = files
    editor = MarkdownEditor([first])
    editor.documents["document-1"].pane.value = "# Unsaved"
    request_close(editor, "document-1")
    row = editor.close_dialog[0][2]
    buttons = [row[key] for key in row.child_keys]
    next(button for button in buttons if button.label == choice)._notify_click()

    assert editor.tabs.child_keys == keys
    assert editor.close_dialog.is_open is False
    assert first.read_text(encoding="utf-8") == written


def test_open_dialog_lists_markdown_files_and_opens_the_pick(files):
    first, _second = files
    editor = MarkdownEditor()
    dialog = editor.open_dialog
    dialog.browse(first.parent)
    listed = [item["label"] for item in dialog.entries.props["items"]]
    dialog.entries.value = str(first)
    picked = dialog.confirm.disabled
    dialog.finish()

    assert listed == ["first.md", "second.md"]
    assert picked is False
    assert [document.path for document in editor.documents.values()] == [first]


def test_new_opens_an_empty_untitled_tab(files):
    first, _second = files
    editor = MarkdownEditor([first])
    editor.menu.callbacks["new"]("new")
    editor.menu.callbacks["new"]("new")
    document = editor.selected

    assert editor.tabs.titles == ["first.md", "untitled-1.md", "untitled-2.md"]
    assert editor.tabs.selected_key == "document-3"
    assert document.path is None
    assert document.pane.value == ""
    assert document.modified is False
    assert path_labels(editor) == ["untitled-2.md"]


def test_saving_a_new_file_asks_for_its_name(files):
    first, _second = files
    editor = MarkdownEditor()
    editor.open_dialog.browse(first.parent)
    editor.new()
    editor.selected.pane.value = "# New"
    editor.menu.callbacks["save"]("save")
    dialog = editor.save_as_dialog
    suggested = (dialog.folder, dialog.name.value)
    dialog.name.value = "fresh"
    dialog.finish()
    fresh = first.parent / "fresh.md"

    assert suggested == (first.parent, "untitled-1.md")
    assert fresh.read_text(encoding="utf-8") == "# New"
    assert editor.selected.path == fresh
    assert editor.tabs.titles == ["fresh.md"]
    assert path_labels(editor) == [*first.parent.parts[1:], "fresh.md"]


def test_save_and_close_of_a_new_file_closes_after_naming_it(files):
    first, _second = files
    editor = MarkdownEditor([first])
    editor.new()
    editor.selected.pane.value = "# New"
    editor.tabs.select_key("document-1")
    request_close(editor, "document-2")
    editor.close_dialog.finish(editor.save_and_close)
    selected = editor.tabs.selected_key
    dialog = editor.save_as_dialog
    dialog.browse(first.parent)
    dialog.name.value = "kept.md"
    dialog.finish()

    assert selected == "document-2"
    assert (first.parent / "kept.md").read_text(encoding="utf-8") == "# New"
    assert editor.tabs.child_keys == ["document-1"]
    assert editor.status.text == "Closed kept.md"
