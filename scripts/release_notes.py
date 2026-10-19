"""Print the GitHub release notes for a version from its CHANGELOG.md section.

GitHub renders every newline in a release description as a line break, so the
hard-wrapped paragraphs and bullets of the changelog are joined into single
lines. A link to the compare view with the previous version ends the notes.

Usage:

    python scripts/release_notes.py 0.2.0
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parents[1] / "CHANGELOG.md"
REPOSITORY = "https://github.com/faysou/anylumino"


def release_notes(changelog: str, version: str) -> str:
    """Return the unwrapped ``version`` section of ``changelog`` with a compare link.

    Raises
    ------
    ValueError
        If ``changelog`` has no ``## <version>`` section.
    """
    versions = re.findall(r"^## (\S+)$", changelog, re.MULTILINE)
    if version not in versions:
        raise ValueError(f"CHANGELOG.md has no '## {version}' section")

    section = changelog.split(f"## {version}\n", 1)[1].split("\n## ", 1)[0]
    blocks: list[str] = []
    for line in section.strip().splitlines():
        if not line.strip():
            blocks.append("")
        elif line.startswith("- ") or not blocks or not blocks[-1]:
            blocks.append(line)
        else:
            blocks[-1] += " " + line.strip()

    notes = "\n".join(blocks)
    index = versions.index(version)
    if index + 1 < len(versions):
        notes += f"\n\n**Full Changelog**: {REPOSITORY}/compare/v{versions[index + 1]}...v{version}"

    return notes + "\n"


if __name__ == "__main__":
    print(release_notes(CHANGELOG.read_text(), sys.argv[1]), end="")
