# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # anylumino Markdown editor
#
# Source on the left, rendered view on the right, one tab per file. The view
# typesets math in the portable forms with KaTeX, inline math between dollar
# signs and backticks and display math in `$$` blocks, and draws `mermaid`
# fences.
# The four Heston papers from crapylib make a stress test: the calibration
# paper alone has about 300 inline expressions, 50 display equations, and
# three Mermaid diagrams with LaTeX labels.

# %%
from pathlib import Path

from anylumino import MarkdownEditor


HESTON_DOCS = Path("~/Developer/nautilus/crapylib/docs/heston").expanduser()

# %%
editor = MarkdownEditor(sorted(HESTON_DOCS.glob("*.md")))
editor.tabs.select(0)
editor

# %%
