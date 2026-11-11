"""Start a JupyterLab server and run notebooks in it through Playwright.

The documentation screenshots in `docs_examples.py` and the browser tests in
`tests/browser` both use this module.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.request
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path

# Page-side checks, run by Playwright inside the JupyterLab page.
NOTEBOOK_READY_JS = """(name) =>
  document.querySelector(".lm-DockPanel-tabBar .lm-TabBar-tab.lm-mod-current .lm-TabBar-tabLabel")
    ?.textContent === name &&
  !!document.querySelector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-CodeCell")"""

# Execution is done once no cell is queued and the kernel has been idle for `idleMs`.
NOTEBOOK_IDLE_JS = """(idleMs) => {
  const panel = document.querySelector(".jp-NotebookPanel:not(.lm-mod-hidden)");
  const prompts = [...panel.querySelectorAll(".jp-CodeCell .jp-InputPrompt")].map((node) => node.textContent.trim());
  const status = panel.querySelector(".jp-Notebook-ExecutionIndicator")?.getAttribute("data-status");
  const ran = prompts.some((prompt) => /^\\[\\d+\\]:$/.test(prompt));
  if (prompts.some((prompt) => prompt.includes("*")) || !ran || status === "busy") {
    window.__idleSince = 0;
    return false;
  }
  window.__idleSince = window.__idleSince || Date.now();
  return Date.now() - window.__idleSince > idleMs;
}"""


@contextmanager
def jupyterlab(
    log_path: Path,
    *,
    root: Path | None = None,
    token: str = "docsshots",
    args: tuple[str, ...] = (),
    env: Mapping[str, str] | None = None,
) -> Iterator[tuple[str, str]]:
    """Run a JupyterLab server on a free port and yield its base URL and token.

    The server serves ``root``, or the working directory when it is omitted.
    ``args`` are extra server options and ``env`` extra environment variables.
    """
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    command = [sys.executable, "-m", "jupyterlab", "--no-browser", f"--port={port}", f"--ServerApp.token={token}"]
    if root is not None:
        command.append(f"--ServerApp.root_dir={root}")

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = log_path.open("w")
    server = subprocess.Popen(
        [*command, *args],
        stdout=log,
        stderr=subprocess.STDOUT,
        env={**os.environ, **(env or {})},
    )
    url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 60
        while True:
            try:
                urllib.request.urlopen(f"{url}/api/status?token={token}", timeout=2)
                break
            except OSError:
                if time.monotonic() > deadline or server.poll() is not None:
                    raise RuntimeError(f"JupyterLab did not start; see {log.name}") from None

                time.sleep(0.5)

        yield url, token
    finally:
        server.terminate()
        server.wait(timeout=30)
        log.close()


def run_notebook(page, url: str, token: str, notebook: str, *, idle_ms: int = 5000) -> None:
    """Open ``notebook``, a path relative to the server root, and run all its cells.

    Raises
    ------
    RuntimeError
        If any cell shows an error output.
    """
    name = notebook.rsplit("/", 1)[-1]
    # A workspace of its own, reset on every run, so JupyterLab opens no
    # notebook that an earlier session left in the default workspace.
    workspace = "".join(char if char.isalnum() else "-" for char in name.rsplit(".", 1)[0])
    page.goto(f"{url}/lab/workspaces/{workspace}/tree/{notebook}?reset&token={token}")
    page.wait_for_function(NOTEBOOK_READY_JS, arg=name, timeout=60_000)
    page.wait_for_timeout(2000)
    page.click('.jp-NotebookPanel:not(.lm-mod-hidden) [data-command="notebook:restart-run-all"]')
    page.click(".jp-Dialog button.jp-mod-accept")
    page.wait_for_function(NOTEBOOK_IDLE_JS, arg=idle_ms, timeout=600_000, polling=250)
    errors = page.locator(".jp-OutputArea-output.jp-mod-error").all_inner_texts()
    if errors:
        raise RuntimeError(f"{notebook}: {len(errors)} cells failed: {errors[0][:300]}")
