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
# so the `fake-agent` session file stays out of `~/.anylumino`. The fake agent
# lives in `fake_agent.py` next to this notebook, which the marimo notebook
# `marimo_workbench_fake_agent.py` shares.
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

import fake_agent


workbench = fake_agent.workbench()
workbench

# %% [markdown]
# The fake agent logs each call. After a restore, the last call starts with
# `exec resume thread-fake`.

# %%
log = fake_agent.WORKDIR / "log.jsonl"
[json.loads(line)["argv"][:3] for line in log.read_text().splitlines()] if log.exists() else []
