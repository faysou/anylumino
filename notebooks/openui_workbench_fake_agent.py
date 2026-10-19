# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # OpenUI workbench with a fake agent

# %% [markdown]
# Checks the workbench end to end without spending agent tokens. A fake
# `codex` executable on `PATH` answers every turn with the same reply: a sales
# explorer program and its callbacks. `HOME` points to a temporary directory,
# so the `fake-agent` session file stays out of `~/.anylumino`.
#
# Run all cells, then type any message in the chat. Check that:
#
# - the four tabs fill (UI, OpenUI, UI code, Callbacks) and the code tabs are
#   read only;
# - the header shows a `Ready` caption, which reads `Running` during the turn;
# - `setup` fills the table with all five `sales` rows, and clicking a column
#   header sorts it;
# - choosing a region updates the heading, badge, and table, and the button
#   writes the total under the table;
# - the UI tab scrolls to the last note paragraph;
# - after a kernel restart and a rerun, the session restores the chat and the
#   tabs, and the next turn resumes thread `thread-fake`.

# %%
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

CALLBACKS = '''def setup(widgets):
    widgets["table"].set_rows(sales.to_dict("records"))


def selected(widgets):
    region = widgets["region"].value or "All"
    return region, sales if region == "All" else sales[sales["region"] == region]


def on_region(event, widgets):
    region, rows = selected(widgets)
    widgets["table"].set_rows(rows.to_dict("records"))
    widgets["status"].label = "All regions" if region == "All" else region
    widgets["title"].text = f"Sales by region: {region}"


def on_total(event, widgets):
    region, rows = selected(widgets)
    widgets["summary"].text = f"Total revenue for {region}: {rows['revenue'].sum():.1f}"
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

# %%
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

# %%
sales = pd.DataFrame(
    {
        "region": ["EMEA", "APAC", "AMER", "EMEA", "APAC"],
        "product": ["Rates", "Rates", "FX", "FX", "Credit"],
        "revenue": [1.5, 2.0, 3.2, 0.8, 1.1],
    }
)

workbench = Workbench(agent="codex", session="fake-agent", namespace={"sales": sales}, cwd=WORKDIR)
workbench

# %% [markdown]
# The fake agent logs each call. After a restore, the last call starts with
# `exec resume thread-fake`.

# %%
log = WORKDIR / "log.jsonl"
[json.loads(line)["argv"][:3] for line in log.read_text().splitlines()] if log.exists() else []
