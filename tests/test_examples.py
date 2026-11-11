import importlib.util
import re
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "docs_examples.py"
# The script imports its sibling modules, as it does when run from the command line.
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location("docs_examples", SCRIPT)
docs_examples = importlib.util.module_from_spec(spec)
# Dataclasses look their module up in sys.modules while the module runs.
sys.modules[spec.name] = docs_examples
spec.loader.exec_module(docs_examples)


@pytest.fixture(autouse=True)
def repo_root(monkeypatch):
    # The script's paths are relative to the repository root.
    monkeypatch.chdir(ROOT)


def test_docs_examples_run():
    source = docs_examples.notebook_source(docs_examples.read_examples())

    exec(compile(source, "docs_examples", "exec"), {})


def test_component_examples_run():
    source = "import anylumino as al\nimport anylumino.astryx as ax\n\n" + "\n\n".join(
        docs_examples.component_cells()
    )

    exec(compile(source, "component_examples", "exec"), {})


def test_readme_examples_run():
    # README fragments use the sample rows and the trend panel the documentation pages define.
    namespace = {}
    exec(compile(docs_examples.NOTEBOOK_HEADER, "header", "exec"), namespace)
    exec(
        compile(docs_examples.SETUP[("index", "Design model", 0)], "setup", "exec"),
        namespace,
    )

    blocks = docs_examples.readme_examples()
    for index, block in enumerate(blocks):
        exec(compile(block, f"README.md block {index}", "exec"), namespace)

    assert len(blocks) == 13


def test_openui_design_note_examples_run():
    blocks = re.findall(r"^```python\n(.*?)^```", (ROOT / "docs" / "openui.md").read_text(), re.S | re.M)

    assert len(blocks) == 2
    for block in blocks:
        exec(compile(block, "openui.md", "exec"), {})
