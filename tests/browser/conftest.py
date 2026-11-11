"""Browser tests: small notebooks run in JupyterLab under headless Chromium.

Every test in this directory carries the ``browser`` marker, which the default
pytest run deselects. Run them with ``make test-browser``, after installing the
browser once with ``uv run --no-sync playwright install chromium``.
"""

from __future__ import annotations

import itertools
import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import nbformat
import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from jupyterlab_runner import jupyterlab, run_notebook  # noqa: E402


# Runs code in the kernel of the open notebook and returns its printed output and any error.
EXECUTE_JS = """async (code) => {
  const kernel = window.jupyterapp.shell.currentWidget.sessionContext.session.kernel;
  const future = kernel.requestExecute({ code, store_history: false });
  let output = "";
  let error = null;
  future.onIOPub = (msg) => {
    const type = msg.header.msg_type;
    if (type === "stream") output += msg.content.text;
    else if (type === "execute_result") output += msg.content.data["text/plain"] ?? "";
    else if (type === "error") error = `${msg.content.ename}: ${msg.content.evalue}`;
  };
  await future.done;
  return { output, error };
}"""

# Sets a trait on the browser's copy of a widget model without telling the kernel,
# as a change made by the widget's own frontend code does before it syncs.
# Finds the notebook's widget manager, which the output renderer holds behind a promise delegate.
FIND_MANAGER_JS = """
  const find = (widget, depth) => {
    if (!widget || depth > 12) return null;
    if (widget._manager?.promise) return widget._manager.promise;
    const children = [...(widget.widgets ?? Array.from(widget.children?.() ?? [])), ...(widget.layout?.widgets ?? [])];
    for (const child of children) {
      const manager = find(child, depth + 1);
      if (manager) return manager;
    }
    return null;
  };
  // Cached on first use, so it is still found after the outputs that held it are cleared.
  window.__anyluminoManager ??= await find(window.jupyterapp.shell.currentWidget.content, 0);
  const manager = window.__anyluminoManager;
"""

# Sets a trait on the browser's copy of a widget model without telling the kernel,
# as a change made by the widget's own frontend code does before it syncs.
SET_FRONTEND_TRAIT_JS = """async ([modelId, name, value]) => {""" + FIND_MANAGER_JS + """
  (await manager.get_model(modelId)).set(name, value);
}"""

# Counts the listeners on a browser model for one event, such as "change:value".
MODEL_LISTENERS_JS = """async ([modelId, event]) => {""" + FIND_MANAGER_JS + """
  const model = await manager.get_model(modelId);
  return (model._events?.[event] ?? []).length;
}"""

# Frontend failures that belong to anylumino rather than to JupyterLab itself.
FRONTEND_ERROR_WORDS = ("anylumino", "astryx", "anywidget", "react", "lumino", "uncaught")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    here = Path(__file__).parent
    for item in items:
        if here in Path(item.fspath).parents:
            item.add_marker(pytest.mark.browser)


class Notebook:
    """A notebook that ran in JupyterLab, with its page and its kernel."""

    def __init__(self, page: Any) -> None:
        self.page = page
        self.console_errors: list[str] = []
        page.on("console", lambda message: message.type == "error" and self.console_errors.append(message.text))
        page.on("pageerror", lambda error: self.console_errors.append(f"uncaught: {error}"))

    def execute(self, code: str) -> str:
        """Run ``code`` in the notebook's kernel and return what it printed."""
        result = self.page.evaluate(EXECUTE_JS, code)
        if result["error"]:
            raise AssertionError(f"kernel error: {result['error']}\n{code}")

        return result["output"]

    def set_frontend_trait(self, model_id: str, name: str, value: Any) -> None:
        """Change trait ``name`` on the browser's model only; the kernel is not told."""
        self.page.evaluate(SET_FRONTEND_TRAIT_JS, [model_id, name, value])

    def model_listeners(self, model_id: str, event: str) -> int:
        """Return how many listeners the browser model ``model_id`` has for ``event``."""
        return self.page.evaluate(MODEL_LISTENERS_JS, [model_id, event])

    def value(self, expression: str) -> Any:
        """Evaluate ``expression`` in the kernel and return it decoded from JSON."""
        return json.loads(self.execute(f"import json as _json\nprint(_json.dumps({expression}))"))

    def output(self, index: int) -> Any:
        """Return a locator for the output area of the code cell at ``index``."""
        return self.page.locator(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-CodeCell").nth(index).locator(
            ".jp-OutputArea-output"
        )

    def frontend_errors(self) -> list[str]:
        """Return console errors and inline child errors raised by widget code."""
        errors = [text for text in self.console_errors if any(word in text.lower() for word in FRONTEND_ERROR_WORDS)]
        errors += self.page.locator(".anylumino-ChildError").all_inner_texts()

        return errors


class Lab:
    def __init__(self, browser: Any, url: str, token: str, root: Path) -> None:
        self.browser = browser
        self.url = url
        self.token = token
        self.root = root
        self.names = itertools.count(1)

    def notebook(self, *cells: str, init_script: str | None = None) -> Notebook:
        """Write ``cells`` as a notebook, run it, and return it once the kernel is idle.

        ``init_script`` runs in the page before JupyterLab loads, such as code that
        instruments browser APIs for a test.
        """
        name = f"test_{next(self.names)}.ipynb"
        document = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(cell) for cell in cells])
        document.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        nbformat.write(document, self.root / name)
        page = self.browser.new_page(viewport={"width": 1180, "height": 900})
        if init_script:
            page.add_init_script(init_script)
        notebook = Notebook(page)
        run_notebook(page, self.url, self.token, name, idle_ms=1000)

        return notebook


@pytest.fixture(scope="session")
def lab(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Lab]:
    from playwright.sync_api import sync_playwright

    base = tmp_path_factory.mktemp("lab")
    root = base / "root"
    settings = base / "settings" / "@jupyterlab" / "notebook-extension"
    root.mkdir()
    settings.mkdir(parents=True)
    # Render every cell, so outputs below the viewport can be inspected.
    (settings / "tracker.jupyterlab-settings").write_text(json.dumps({"windowingMode": "none"}))
    env = {
        "JUPYTERLAB_SETTINGS_DIR": str(base / "settings"),
        "JUPYTERLAB_WORKSPACES_DIR": str(base / "workspaces"),
    }
    with (
        jupyterlab(base / "lab.log", root=root, token="browsertests", args=("--LabApp.expose_app_in_browser=True",), env=env) as (url, token),
        sync_playwright() as playwright,
    ):
        browser = playwright.chromium.launch()
        try:
            yield Lab(browser, url, token, root)
        finally:
            browser.close()


@pytest.fixture
def notebook(lab: Lab) -> Iterator[Any]:
    """Return a function that runs cells as a notebook; its pages close after the test."""
    opened: list[Notebook] = []

    def run(*cells: str, init_script: str | None = None) -> Notebook:
        opened.append(lab.notebook(*cells, init_script=init_script))

        return opened[-1]

    yield run
    for item in opened:
        item.page.close()
