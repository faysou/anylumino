# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Astryx theme smoke test
#
# This notebook exercises runtime Astryx themes and a precompiled-style
# `BuiltTheme` descriptor inside JupyterLab output areas.

# %%
from __future__ import annotations

import anylumino.astryx as ax


runtime_blue = ax.Brand(
    "runtime-blue",
    **{
        "color-accent": ("#0057b8", "#79b8ff"),
        "color-background-card": ("#ffffff", "#111827"),
        "color-text-primary": ("#111827", "#f9fafb"),
        "radius-container": "8px",
    },
)

runtime_green = ax.Brand(
    "runtime-green",
    **{
        "color-accent": ("#0f7b43", "#7be0a3"),
        "color-background-card": ("#f8fff9", "#07190f"),
        "color-text-primary": ("#102116", "#f1fff5"),
        "radius-container": "10px",
    },
)

built_css = """
@layer astryx-theme {
  @scope([data-astryx-theme="built-plum"]) to ([data-astryx-theme]) {
    :scope {
      --color-accent: light-dark(#7c2d92, #e7a8ff);
      --color-background-card: light-dark(#fff7ff, #1c0d22);
      --color-background-surface: light-dark(#ffffff, #24102c);
      --color-text-primary: light-dark(#24102c, #fff7ff);
      --color-text-secondary: light-dark(#724a7b, #d7b7df);
      --radius-container: 12px;
    }
  }
}
"""

built_plum = ax.BuiltTheme(
    "built-plum",
    css=built_css,
    tokens={
        "color-accent": ("#7c2d92", "#e7a8ff"),
        "color-background-card": ("#fff7ff", "#1c0d22"),
        "color-text-primary": ("#24102c", "#fff7ff"),
    },
)


def theme_panel(title: str, theme: dict[str, object], mode: str) -> ax.Theme:
    return ax.Theme(
        ax.Card(
            ax.Stack(
                {
                    "title": ax.Heading(title, level=3),
                    "body": ax.Text(
                        f"mode={mode}", type="supporting", color="secondary"
                    ),
                    "actions": ax.Stack(
                        {
                            "button": ax.Button("Primary", variant="primary"),
                            "badge": ax.Badge("Ready", variant="success"),
                            # StatusDot renders only the dot and exposes its
                            # label to screen readers, so the caption is a Text.
                            "status": ax.StatusDot("Connected", variant="success"),
                            "status_label": ax.Text("Connected"),
                        },
                        direction="horizontal",
                        gap=2,
                        align="center",
                        wrap="wrap",
                    ),
                    "progress": ax.ProgressBar(72, label="Coverage", value_label=True),
                },
                gap=2,
            ),
            width="100%",
            padding=4,
        ),
        brand=theme,
        mode=mode,
        width="100%",
    )


themes = ax.Grid(
    {
        "runtime_light": theme_panel("Runtime blue light", runtime_blue, "light"),
        "runtime_dark": theme_panel("Runtime blue dark", runtime_blue, "dark"),
        "runtime_system": theme_panel("Runtime green system", runtime_green, "system"),
        "runtime_lab": theme_panel("Runtime green JupyterLab", runtime_green, "jupyterlab"),
        "built_plum": theme_panel("Built plum system", built_plum, "system"),
        "built_lab": theme_panel("Built plum JupyterLab", built_plum, "jupyterlab"),
    },
    columns={"minWidth": 260, "repeat": "fit"},
    gap=3,
    width="100%",
)

themes

# %%
assert runtime_blue["name"] == "runtime-blue"
assert built_plum["built"] is True
assert built_plum["name"] == "built-plum"
assert 'data-astryx-theme="built-plum"' in built_plum["css"]
assert themes.props["columns"] == {"minWidth": 260, "repeat": "fit"}
assert themes["runtime_lab"].color_mode == "jupyterlab"
assert themes["runtime_lab"].get_widget("widget-1").color_mode == "jupyterlab"
