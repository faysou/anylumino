"""Dialogs that browse the kernel's folders to export the workbench's file or import one."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from anylumino import astryx as ax

from .export import file_name


def run_now(call: Callable[[], None]) -> None:
    call()


class FolderDialog(ax.Dialog):
    """Browse the kernel's folders, with ``fields`` under the folder list and a confirm button.

    The dialog browses the kernel's file system, not the browser's, because
    the kernel writes and reads the files. With ``suffix``, files with that
    suffix are listed after the folders, and clicking one calls `pick`.
    Browsing builds a button per entry, so it runs through ``run``, which
    calls it at once by default; marimo creates widgets only from work a
    cell started, so a workbench in marimo passes its turn loop.
    """

    def __init__(
        self,
        title: str,
        fields: Sequence[ax.Widget],
        confirm: str,
        suffix: str = "",
        run: Callable[[Callable[[], None]], None] = run_now,
    ) -> None:
        self.suffix = suffix
        self.run = run
        self.folder: Path | None = None
        self.path = ax.Text("", text_type="supporting")
        self.folders = ax.Stack([], direction="vertical", gap=0, height=220, scrollable=True)
        up = ax.Button(
            "Up", variant="ghost", size="sm", callbacks=[lambda _button: self.run(lambda: self.browse(self.folder.parent))]
        )
        cancel = ax.Button("Cancel", callbacks=[lambda _button: self.hide()])
        self.confirm = ax.Button(confirm, variant="primary", callbacks=[lambda _button: self.finish()])
        super().__init__(
            ax.Stack(
                [
                    ax.Heading(title),
                    ax.Stack([self.path, up], direction="horizontal", justify="between", align="center"),
                    self.folders,
                    *fields,
                    ax.Stack([cancel, self.confirm], direction="horizontal", justify="end"),
                ],
                direction="vertical",
                gap=3,
                padding=4,
            ),
            open=False,
            inline=False,
        )
        # Set as a prop only: the width argument also sizes the widget host, which then
        # takes header space while the dialog is closed
        self.props = {**self.props, "width": 480}

    def open_in_last_folder(self) -> None:
        """Show the dialog in the last browsed folder, or the current directory at the first open."""
        self.run(lambda: self.browse(self.folder or Path.cwd()))
        self.show()

    def browse(self, folder: Path) -> None:
        self.folder = folder.resolve()
        self.path.text = str(self.folder)
        try:
            entries = sorted(
                (entry for entry in self.folder.iterdir() if not entry.name.startswith(".")), key=lambda entry: entry.name
            )
        except OSError:
            entries = []

        folders = [
            ax.Button(f"{entry.name}/", variant="ghost", size="sm", callbacks=[lambda _button, entry=entry: self.run(lambda: self.browse(entry))])
            for entry in entries
            if entry.is_dir()
        ]
        files = [
            ax.Button(entry.name, variant="ghost", size="sm", callbacks=[lambda _button, entry=entry: self.pick(entry)])
            for entry in entries
            if self.suffix and entry.is_file() and entry.suffix == self.suffix
        ]
        self.folders.widgets = [*folders, *files]
        self.browsed()

    def browsed(self) -> None:
        """Update the fields after the folder changes."""

    def pick(self, path: Path) -> None:
        """Handle a click on a listed file."""

    def finish(self) -> None:
        """Handle the confirm button."""


class ExportDialog(FolderDialog):
    """Pick a folder and a name, then call ``on_export(path)`` with the file in that folder."""

    def __init__(self, on_export: Callable[[Path], None], run: Callable[[Callable[[], None]], None] = run_now) -> None:
        self.on_export = on_export
        self.name = ax.TextInput("ui", label="Name")
        self.files = ax.Text("", text_type="supporting")
        super().__init__("Export UI", [self.name, self.files], "Export", run=run)
        self.name.observe(lambda _change: self.browsed(), names="value")

    def open_with(self, name: str) -> None:
        """Show the dialog with ``name`` filled in, in the last browsed folder or the current directory."""
        self.name.value = name
        self.open_in_last_folder()

    def browsed(self) -> None:
        self.files.text = f"Writes {file_name(self.name.value or 'ui')} here, replacing an existing file."

    def finish(self) -> None:
        self.hide()
        self.on_export(self.folder / file_name(self.name.value or "ui"))


class ImportDialog(FolderDialog):
    """Pick an exported ``.py`` file, then call ``on_import(path)``."""

    def __init__(self, on_import: Callable[[Path], None], run: Callable[[Callable[[], None]], None] = run_now) -> None:
        self.on_import = on_import
        self.chosen: Path | None = None
        self.files = ax.Text("", text_type="supporting")
        super().__init__("Import UI", [self.files], "Import", suffix=".py", run=run)

    def browsed(self) -> None:
        self.chosen = None
        self.files.text = "Pick an exported file."
        self.confirm.disabled = True

    def pick(self, path: Path) -> None:
        self.chosen = path
        self.files.text = f"Imports {path.name} into the workbench, replacing the current UI."
        self.confirm.disabled = False

    def finish(self) -> None:
        self.hide()
        self.on_import(self.chosen)
