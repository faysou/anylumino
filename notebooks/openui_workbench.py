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
# # OpenUI workbench

# %% [markdown]
# Chat with `claude` or `codex` on the left to build a UI on the right. The
# `sales` data frame is in the namespace, so callbacks can read it. Set
# `AGENT` to the CLI you have signed in to. Every turn spends agent tokens.

# %%
import pandas as pd

from anylumino.workbench import Workbench


AGENT = "claude"

sales = pd.DataFrame(
    {
        "region": ["EMEA", "APAC", "AMER", "EMEA", "APAC"],
        "product": ["Rates", "Rates", "FX", "FX", "Credit"],
        "revenue": [1.5, 2.0, 3.2, 0.8, 1.1],
    }
)

workbench = Workbench(agent=AGENT, session="sales-demo", namespace={"sales": sales})
workbench

# %% [markdown]
# Try: "Show the sales table, a region selector, and a button that writes the
# total revenue of the selected region under the table."
