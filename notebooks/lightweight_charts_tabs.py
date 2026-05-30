# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # anylumino tab smoke test
#
# This notebook exercises `anylumino.TabPanel`, an anywidget container whose
# frontend uses Lumino's `TabPanel` layout widget.

# %%
from __future__ import annotations

from pathlib import Path
import os
import sys

import pandas as pd

from anylumino import TabPanel, TextWidget


def get_notebook_path() -> Path:
    try:
        from IPython import get_ipython

        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return Path(os.path.abspath(""))
    except (ImportError, NameError):
        pass
    return Path(__file__).resolve().parent


def find_nautilus_root() -> Path:
    notebook_path = get_notebook_path().resolve()
    return next(
        path for path in [notebook_path, *notebook_path.parents]
        if (path / "lightweight-charts-python").exists()
    )


# %% [markdown]
# ## Basic anywidget children

# %%
TabPanel(
    [
        TextWidget("This is an anywidget child rendered in a Lumino tab."),
        TextWidget("The second tab is a separate child widget."),
    ],
    titles=["First", "Second"],
    width="100%",
    height=260,
)

# %% [markdown]
# ## lightweight-charts-python children
#
# This section uses the sibling `lightweight-charts-python` checkout as a POC
# child widget provider.

# %%
nautilus_root = find_nautilus_root()
lightweight_charts_repo = nautilus_root / "lightweight-charts-python"
if str(lightweight_charts_repo) not in sys.path:
    sys.path.insert(0, str(lightweight_charts_repo))

from lightweight_charts_esistjosh import NotebookChart  # noqa: E402


data_path = lightweight_charts_repo / "examples" / "1_setting_data" / "ohlcv.csv"
data = pd.read_csv(data_path)

chart_a = NotebookChart(width="100%", height="100%", toolbox=False)
chart_a.set(data)

chart_b = NotebookChart(width="100%", height="100%", toolbox=False)
chart_b.set(data.tail(80))

chart_tabs = TabPanel(
    [chart_a.widget],
    titles=["Full sample"],
    selected_index=0,
    width="100%",
    height=520,
)

chart_tabs

# %% [markdown]
# ## Add a chart tab after display

# %%
chart_tabs.add_tab(chart_b.widget, "Recent sample", select=True)

# %%
