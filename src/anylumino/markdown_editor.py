"""Edit Markdown files with a live preview, one tab per file."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from anylumino import astryx as ax
from anylumino.file_dialogs import FolderDialog
from anylumino.layout import MenuBar, TabPanel

MARKDOWN_SUFFIX = ".md"


class OpenDialog(FolderDialog):
    """Pick a Markdown file, then call ``on_open(path)``."""

    def __init__(self, on_open: Callable[[Path], None]) -> None:
        self.on_open = on_open
        self.chosen: Path | None = None
        self.files = ax.Text("", text_type=ax.TextType.SUPPORTING)
        super().__init__("Open Markdown", [self.files], "Open", suffix=MARKDOWN_SUFFIX)

    def browsed(self) -> None:
        self.chosen = None
        self.files.text = "Pick a Markdown file."
        self.confirm.disabled = True

    def pick(self, path: Path) -> None:
        self.chosen = path
        self.files.text = f"Opens {path.name} in a new tab."
        self.confirm.disabled = False

    def finish(self) -> None:
        self.hide()
        self.on_open(self.chosen)


class SaveAsDialog(FolderDialog):
    """Pick a folder and a name, then call ``on_save_as(path)`` with the file in that folder."""

    def __init__(self, on_save_as: Callable[[Path], None]) -> None:
        self.on_save_as = on_save_as
        self.name = ax.TextInput("", label="Name")
        self.files = ax.Text("", text_type=ax.TextType.SUPPORTING)
        super().__init__("Save Markdown as", [self.name, self.files], "Save", suffix=MARKDOWN_SUFFIX)
        self.name.observe(lambda _change: self.browsed(), names="value")

    def open_with(self, path: Path) -> None:
        """Show the dialog in the folder of ``path`` with its name filled in."""
        self.name.value = path.name
        self.run(lambda: self.browse(path.parent))
        self.show()

    def chosen(self) -> str:
        name = self.name.value.strip()
        return name if not name or Path(name).suffix else f"{name}{MARKDOWN_SUFFIX}"

    def browsed(self) -> None:
        name = self.chosen()
        self.files.text = f"Writes {name} here, replacing an existing file." if name else "Enter a file name."
        self.confirm.disabled = not name

    def pick(self, path: Path) -> None:
        self.name.value = path.name

    def finish(self) -> None:
        self.hide()
        self.on_save_as(self.folder / self.chosen())


class CloseDialog(ax.Dialog):
    """Ask what to do with the unsaved changes of a tab being closed."""

    def __init__(self, on_save: Callable[[str], None], on_discard: Callable[[str], None]) -> None:
        self.key: str | None = None
        self.message = ax.Text("")
        save = ax.Button("Save and close", variant=ax.ButtonVariant.PRIMARY, callbacks=[lambda _button: self.finish(on_save)])
        discard = ax.Button("Discard changes", callbacks=[lambda _button: self.finish(on_discard)])
        cancel = ax.Button("Cancel", variant=ax.ButtonVariant.GHOST, callbacks=[lambda _button: self.hide()])
        super().__init__(
            ax.Stack(
                [
                    ax.Heading("Unsaved changes"),
                    self.message,
                    ax.Stack([cancel, discard, save], direction=ax.Orientation.HORIZONTAL, justify=ax.Justify.END),
                ],
                direction=ax.Orientation.VERTICAL,
                gap=3,
                padding=4,
            ),
            open=False,
            inline=False,
        )
        # The width the folder dialogs use, so the three buttons fit on one row. It is set as a
        # prop only: the width argument also sizes the widget host, which takes space while closed.
        self.props = {**self.props, "width": 480}

    def ask(self, key: str, name: str) -> None:
        self.key = key
        self.message.text = f"{name} has unsaved changes. Close it anyway?"
        self.show()

    def finish(self, action: Callable[[str], None]) -> None:
        self.hide()
        action(self.key)


class MarkdownDocument:
    """One open file, or a new one named ``name`` with no ``path`` until saved, edited in a `MarkdownEditorPane`."""

    def __init__(self, path: Path | None, name: str = "") -> None:
        self.path = path
        self.name = path.name if path else name
        self.saved = path.read_text(encoding="utf-8") if path else ""
        self.pane = ax.MarkdownEditorPane(self.saved, height="100%")

    @property
    def modified(self) -> bool:
        return self.pane.value != self.saved

    @property
    def title(self) -> str:
        return f"* {self.name}" if self.modified else self.name

    def save(self) -> None:
        self.path.write_text(self.pane.value, encoding="utf-8")
        self.saved = self.pane.value


class MarkdownEditor:
    """Edit Markdown files side by side with their rendered view.

    Each open file gets a tab with a `MarkdownEditorPane`: highlighted source
    on the left and the rendered Markdown, math and Mermaid diagrams
    included, on the right, aligned to the caret line. The File menu starts
    a new file, opens a ``.md`` file from the kernel's folders, saves the
    selected tab, or saves it under a new name, and shows each command's
    keyboard shortcut. A new file asks for its name at its first save. The
    path of the selected file shows under the menu.
    A tab title starts with ``*`` while its text differs from the saved file, and
    closing such a tab asks whether to save or discard them.

    Examples
    --------
    ```python
    MarkdownEditor(["notes.md"])
    ```

    Parameters
    ----------
    paths : Iterable[str | Path], default ()
        Files to open at start, one tab each.
    height : int, default 760
        Height of the tabs and their panes in pixels.
    """

    def __init__(self, paths: Iterable[str | Path] = (), *, height: int = 760) -> None:
        self.documents: dict[str, MarkdownDocument] = {}
        self.opened = 0
        self.created = 0
        self.closing_after_save: str | None = None
        self.tabs = TabPanel([], tabs_closable=True, height=height, resizable=False)
        self.tabs.on_tab_close(lambda _panel, key: self.close(key))
        self.tabs.observe(lambda _change: self.switched(), names="selected_index")
        self.menu = MenuBar(
            [
                {
                    "label": "File",
                    "items": [
                        # Browsers keep Cmd N and Cmd Alt N on macOS for windows; Ctrl Alt N is free everywhere.
                        {"id": "new", "label": "New", "icon": "AddContent", "shortcut": "Ctrl Alt N"},
                        {"id": "open", "label": "Open...", "icon": "FolderOpen", "shortcut": "Accel O"},
                        {"id": "save", "label": "Save", "icon": "Save", "shortcut": "Accel S"},
                        {"id": "save_as", "label": "Save as...", "icon": "SaveAs", "shortcut": "Accel Shift S"},
                    ],
                }
            ],
            callbacks={
                "new": lambda _item: self.new(),
                "open": lambda _item: self.open_dialog.open_in_last_folder(),
                "save": lambda _item: self.save(),
                "save_as": lambda _item: self.ask_save_as(),
            },
        )
        self.path = ax.Breadcrumbs([], variant=ax.BreadcrumbsVariant.SUPPORTING, separator="/", label="File path")
        self.status = ax.Text("", text_type=ax.TextType.SUPPORTING)
        self.open_dialog = OpenDialog(self.open)
        self.save_as_dialog = SaveAsDialog(self.save_as)
        self.close_dialog = CloseDialog(self.save_and_close, self.discard)
        self.widget = ax.Stack(
            [
                self.menu,
                ax.Stack(
                    [self.path, self.status],
                    direction=ax.Orientation.HORIZONTAL,
                    justify=ax.Justify.BETWEEN,
                    align=ax.Align.CENTER,
                    padding=1,
                    # The tab bar's colors, so the menu, path, and tabs read as one header.
                    style={"background": "#eef2f7", "border": "1px solid #d8dee9", "borderTop": "none"},
                ),
                self.tabs,
                self.open_dialog,
                self.save_as_dialog,
                self.close_dialog,
            ],
            direction=ax.Orientation.VERTICAL,
            gap=0,
        )
        for path in paths:
            self.open(path)

    def _repr_mimebundle_(self, **kwargs: Any) -> Any:
        return self.widget._repr_mimebundle_(**kwargs)

    @property
    def selected(self) -> MarkdownDocument | None:
        key = self.tabs.selected_key
        return None if key is None else self.documents[key]

    def new(self) -> None:
        """Start an empty file in a new tab, named ``untitled-N.md`` until its first save."""
        self.created += 1
        self.add(MarkdownDocument(None, f"untitled-{self.created}{MARKDOWN_SUFFIX}"))
        self.status.text = ""

    def open(self, path: str | Path) -> None:
        """Open ``path`` in a new tab, or select its tab when it is already open."""
        path = Path(path).resolve()
        key = next((key for key, document in self.documents.items() if document.path == path), None)
        if key is None:
            self.add(MarkdownDocument(path))
        else:
            self.tabs.select_key(key)
        self.status.text = f"Opened {path.name}"

    def add(self, document: MarkdownDocument) -> None:
        self.opened += 1
        key = f"document-{self.opened}"
        document.pane.observe(lambda _change: self.retitle(key), names="value")
        self.documents[key] = document
        self.tabs.add_tab(document.pane, document.name, key=key)
        self.tabs.select_key(key)
        self.show_path()

    def save(self) -> None:
        """Write the selected tab to its file, asking for a name when it has none yet."""
        document = self.selected
        if document is None:
            return
        if document.path is None:
            self.ask_save_as()
            return
        document.save()
        self.retitle(self.tabs.selected_key)
        self.status.text = f"Saved {document.name}"

    def ask_save_as(self, closing: str | None = None) -> None:
        document = self.selected
        if document is None:
            return
        self.closing_after_save = closing
        folder = self.save_as_dialog.folder or self.open_dialog.folder or Path.cwd()
        self.save_as_dialog.open_with(document.path or folder / document.name)

    def save_as(self, path: Path) -> None:
        """Write the selected tab to ``path`` and keep editing it there."""
        document = self.selected
        if document is None:
            return
        document.path = path.resolve()
        document.name = document.path.name
        self.save()
        self.show_path()
        if self.closing_after_save == self.tabs.selected_key:
            self.discard(self.closing_after_save)
        self.closing_after_save = None

    def close(self, key: str) -> None:
        """Close the tab of ``key``, asking first when its file has unsaved changes."""
        document = self.documents[key]
        if document.modified:
            self.close_dialog.ask(key, document.name)
            return
        self.discard(key)

    def save_and_close(self, key: str) -> None:
        if self.documents[key].path is None:
            self.tabs.select_key(key)
            self.ask_save_as(closing=key)
            return
        self.documents[key].save()
        self.discard(key)

    def discard(self, key: str) -> None:
        document = self.documents.pop(key)
        self.tabs.remove_widget(key, close=True)
        self.show_path()
        self.status.text = f"Closed {document.name}"

    def retitle(self, key: str) -> None:
        """Start the tab title with ``*`` while its text differs from the saved file."""
        index = self.tabs.child_keys.index(key)
        title = self.documents[key].title
        if self.tabs.titles[index] != title:
            self.tabs.titles = [*self.tabs.titles[:index], title, *self.tabs.titles[index + 1 :]]

    def switched(self) -> None:
        self.status.text = ""
        self.show_path()

    def show_path(self) -> None:
        """Show the folders and name of the selected file under the menu."""
        document = self.selected
        # The first part is the root, which the separators already show. A new file shows its name alone.
        parts = () if document is None else (document.path.parts[1:] if document.path else (document.name,))
        items = [{"label": part} for part in parts[:-1]] + [{"label": part, "current": True} for part in parts[-1:]]
        self.path.props = {**self.path.props, "items": items}
