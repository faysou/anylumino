"""Dialogs that browse the kernel's folders to export the workbench's file or import one."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from anylumino import astryx as ax
from anylumino.file_dialogs import FolderDialog, run_now

from .export import file_name


class ExportDialog(FolderDialog):
    """Pick a folder and a name, then call ``on_export(path)`` with the file in that folder."""

    def __init__(self, on_export: Callable[[Path], None], run: Callable[[Callable[[], None]], None] = run_now) -> None:
        self.on_export = on_export
        self.name = ax.TextInput("ui", label="Name")
        self.files = ax.Text("", text_type=ax.TextType.SUPPORTING)
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
        self.files = ax.Text("", text_type=ax.TextType.SUPPORTING)
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
