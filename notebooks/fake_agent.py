"""A workbench answered by a fake `codex`, for checking the workbench without spending agent tokens.

The fake `codex` on `PATH` answers every turn with the same reply: a sales
explorer program and its callbacks. It logs each call to `WORKDIR / "log.jsonl"`.
`HOME` points to a temporary directory, so the `fake-agent` session file stays
out of `~/.anylumino`. The notebooks that use it import it from this folder.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd

from anylumino.workbench import Workbench


WORKDIR = Path(tempfile.gettempdir()) / "anylumino-workbench-fake-agent"

NOTES = "\n\n".join(f"Note paragraph {n}: revenue figures are in millions." for n in range(1, 13))

PROGRAM = """root = VBox([title, tabs, notes])
title = Heading("Sales by region")
tabs = TabPanel([explore, about], ["Explore", "About"], {fit_content: true})
explore = VBox([controls, table, summary])
controls = HBox([region, total, status], null, {align: "end"})
region = Selector(["All", "EMEA", "APAC", "AMER"], "All", "Region", @Callback("on_region"))
total = Button("Total revenue", @Callback("on_total"))
status = Badge("All regions", "info")
table = Table([], ["region", "product", "revenue"], {sortable: true, striped: true})
summary = Text("Pick a region, then press Total revenue.")
about = Markdown("Data comes from the `sales` frame in the namespace.")
notes = Markdown(""" + json.dumps(NOTES) + ")"

CALLBACKS = '''from anylumino.workbench import App


class SalesApp(App):
    def setup(self):
        self.ui.table.set_rows(self.sales.to_dict("records"))

    def selected(self):
        region = self.ui.region.value or "All"
        return region, self.sales if region == "All" else self.sales[self.sales["region"] == region]

    def on_region(self, event):
        region, rows = self.selected()
        self.ui.table.set_rows(rows.to_dict("records"))
        self.ui.status.label = "All regions" if region == "All" else region
        self.ui.title.text = f"Sales by region: {region}"

    def on_total(self, event):
        region, rows = self.selected()
        self.ui.summary.text = f"Total revenue for {region}: {rows['revenue'].sum():.1f}"
'''

REPLY = (
    "Here is a sales explorer with a region selector and a total button.\n\n"
    f"```openui-lang\n{PROGRAM}\n```\n\n"
    f"```python\n{CALLBACKS}```"
)

FAKE_CODEX = f"""#!{sys.executable}
import json, os, sys
if sys.argv[1:3] == ["mcp", "list"]:
    sys.exit(print("[]"))
prompt = sys.stdin.read()
with open(os.environ["FAKE_LOG"], "a") as log:
    log.write(json.dumps({{"argv": sys.argv[1:], "prompt": prompt}}) + "\\n")
sys.stdout.write(open(os.environ["FAKE_STREAM"]).read())
"""

SALES = pd.DataFrame(
    {
        "region": ["EMEA", "APAC", "AMER", "EMEA", "APAC"],
        "product": ["Rates", "Rates", "FX", "FX", "Credit"],
        "revenue": [1.5, 2.0, 3.2, 0.8, 1.1],
    }
)


def workbench() -> Workbench:
    """Install the fake `codex` and return a workbench on it, with `SALES` as `sales` in the namespace."""
    (WORKDIR / "bin").mkdir(parents=True, exist_ok=True)
    codex = WORKDIR / "bin" / "codex"
    codex.write_text(FAKE_CODEX)
    codex.chmod(0o755)
    events = [
        {"type": "thread.started", "thread_id": "thread-fake"},
        {"type": "item.completed", "item": {"id": "item_0", "type": "agent_message", "text": REPLY}},
        {"type": "turn.completed"},
    ]
    (WORKDIR / "stream.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))

    os.environ["PATH"] = f"{WORKDIR / 'bin'}{os.pathsep}{os.environ['PATH']}"
    os.environ["FAKE_STREAM"] = str(WORKDIR / "stream.jsonl")
    os.environ["FAKE_LOG"] = str(WORKDIR / "log.jsonl")
    os.environ["HOME"] = str(WORKDIR / "home")

    return Workbench(agent="codex", session="fake-agent", namespace={"sales": SALES}, cwd=WORKDIR)
