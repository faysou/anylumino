"""Dialogs that browse the kernel's folders to pick a file to read or a place to write one."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from anylumino import astryx as ax


def run_now(call: Callable[[], None]) -> None:
    call()


class FolderDialog(ax.Dialog):
    """Browse the kernel's folders, with ``fields`` under the folder list and a confirm button.

    The dialog browses the kernel's file system, not the browser's, because
    the kernel writes and reads the files. With ``suffix``, files with that
    suffix are listed after the folders, and clicking one calls `pick`. The
    entries are items of one clickable list, so a folder with many entries
    costs a single update. Browsing runs through ``run``, which calls it at
    once by default; a workbench in marimo passes its turn loop.
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
        self.path = ax.Text("", text_type=ax.TextType.SUPPORTING)
        self.listed: dict[str, Path] = {}
        self.entries = ax.List([], density=ax.Density.COMPACT, clickable=True)
        self.entries.observe(self.clicked, names="value")
        up = ax.Button(
            "Up", variant=ax.ButtonVariant.GHOST, size=ax.Size.SM, callbacks=[lambda _button: self.run(lambda: self.browse(self.folder.parent))]
        )
        cancel = ax.Button("Cancel", callbacks=[lambda _button: self.hide()])
        self.confirm = ax.Button(confirm, variant=ax.ButtonVariant.PRIMARY, callbacks=[lambda _button: self.finish()])
        super().__init__(
            ax.Stack(
                [
                    # Up shares the title row, so a long path on its own line never squeezes it.
                    ax.Stack([ax.Heading(title), up], direction=ax.Orientation.HORIZONTAL, justify=ax.Justify.BETWEEN, align=ax.Align.CENTER),
                    self.path,
                    ax.Stack([self.entries], direction=ax.Orientation.VERTICAL, gap=0, height=220, scrollable=True),
                    *fields,
                    ax.Stack([cancel, self.confirm], direction=ax.Orientation.HORIZONTAL, justify=ax.Justify.END),
                ],
                direction=ax.Orientation.VERTICAL,
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

        folders = [entry for entry in entries if entry.is_dir()]
        files = [entry for entry in entries if self.suffix and entry.is_file() and entry.suffix == self.suffix]
        self.listed = {str(entry): entry for entry in [*folders, *files]}
        items = [{"label": f"{entry.name}/", "value": str(entry)} for entry in folders]
        items += [{"label": entry.name, "value": str(entry)} for entry in files]
        self.entries.value = None
        self.entries.props = {**self.entries.props, "items": items}
        self.browsed()

    def clicked(self, change: dict[str, object]) -> None:
        entry = self.listed.get(change["new"])
        if entry is None:
            return
        if entry.is_dir():
            self.run(lambda: self.browse(entry))
        else:
            # Cleared so a second click on the same file still counts.
            self.entries.value = None
            self.pick(entry)

    def browsed(self) -> None:
        """Update the fields after the folder changes."""

    def pick(self, path: Path) -> None:
        """Handle a click on a listed file."""

    def finish(self) -> None:
        """Handle the confirm button."""
