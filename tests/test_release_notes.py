import importlib.util
import tomllib
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "release_notes.py"
spec = importlib.util.spec_from_file_location("release_notes", SCRIPT)
release_notes_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_notes_module)

release_notes = release_notes_module.release_notes

CHANGELOG = """# Changelog

## 0.3.0

This release adds charts:
plotting from the chat.

- Added `Plot`, which builds a
  Plotly figure.
- Fixed a bug.

## 0.2.0

- First notes.
"""


def test_notes_unwrap_paragraphs_and_bullets_and_link_the_previous_version():
    assert release_notes(CHANGELOG, "0.3.0") == (
        "This release adds charts: plotting from the chat.\n"
        "\n"
        "- Added `Plot`, which builds a Plotly figure.\n"
        "- Fixed a bug.\n"
        "\n"
        "**Full Changelog**: https://github.com/faysou/anylumino/compare/v0.2.0...v0.3.0\n"
    )


def test_the_oldest_version_has_no_compare_link():
    assert release_notes(CHANGELOG, "0.2.0") == "- First notes.\n"


def test_a_version_without_a_section_is_rejected():
    with pytest.raises(ValueError, match="^CHANGELOG.md has no '## 0.4.0' section$"):
        release_notes(CHANGELOG, "0.4.0")


def test_the_project_version_has_changelog_notes():
    root = Path(__file__).resolve().parents[1]
    version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]

    notes = release_notes((root / "CHANGELOG.md").read_text(), version)

    assert notes.splitlines()[0].strip() != ""
