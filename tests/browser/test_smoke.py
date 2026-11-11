import os
from pathlib import Path

import jupytext


ROOT = Path(__file__).resolve().parents[2]


# Widgets render after their bundle arrives; wait until no output still shows the loading text.
RENDERED_JS = """() => ![...document.querySelectorAll(".jp-OutputArea-output")].some((node) =>
  node.textContent.includes("Loading widget"))"""


def component_cells():
    import docs_examples

    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        return docs_examples.component_cells()
    finally:
        os.chdir(cwd)


def smoke_notebook_cells():
    document = jupytext.read(ROOT / "notebooks" / "astryx_components_smoke.py")

    return [cell.source for cell in document.cells if cell.cell_type == "code"]


def assert_renders_cleanly(nb):
    nb.page.wait_for_function(RENDERED_JS, timeout=60_000)
    nb.page.wait_for_timeout(3000)

    assert nb.frontend_errors() == []


def test_every_component_example_renders(notebook):
    nb = notebook("import anylumino as al\nimport anylumino.astryx as ax", *component_cells())

    assert_renders_cleanly(nb)


def test_components_smoke_notebook_renders(notebook):
    nb = notebook(*smoke_notebook_cells())

    assert_renders_cleanly(nb)
