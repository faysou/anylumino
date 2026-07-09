# Astryx brand and theme wrappers

`AstryxBrand` and `AstryxTheme` provide a reusable way to apply Astryx design
tokens to notebook widgets without passing style-related props to each
component.

## AstryxBrand

`AstryxBrand` creates a JSON-safe Astryx theme token record that can be synced
to the frontend.

```python
import anylumino as al

brand = al.AstryxBrand(
    "trading-desk",
    **{
        "color-accent": ("#0057b8", "#79b8ff"),
        "color-background-card": ("#ffffff", "#111827"),
        "color-text-primary": ("#111827", "#f9fafb"),
        "radius-container": "8px",
    },
)
```

The result is a dictionary shaped like this:

```python
{
    "name": "trading-desk",
    "tokens": {
        "color-accent": ["#0057b8", "#79b8ff"],
        "color-background-card": ["#ffffff", "#111827"],
        "color-text-primary": ["#111827", "#f9fafb"],
        "radius-container": "8px",
    },
}
```

Token names may include or omit the CSS custom property prefix. The frontend
normalizes `color-accent` to `--color-accent` before calling Astryx
`defineTheme()`.

Token values can be strings or two-item light/dark tuples. For example,
`("white", "black")` becomes a mode-aware token value.

## AstryxTheme

`AstryxTheme` applies a brand and color mode to a subtree of Astryx widgets.
It renders as an Astryx `Stack`, so it also accepts layout options such as
`direction` and `gap`.

```python
app = al.AstryxTheme(
    {
        "header": header,
        "controls": controls,
        "table": table,
    },
    brand=brand,
    color_mode="light",
    gap=3,
)
```

The wrapper applies the brand to itself and recursively to nested
`AstryxWidget` children:

```python
button = al.AstryxButton("Refresh")
panel = al.AstryxTheme([button], brand=brand, color_mode="dark")

assert panel.brand == brand
assert button.brand == brand
assert button.color_mode == "dark"
```

This propagation is necessary in notebooks because each anywidget child is
mounted in its own frontend root. A normal React theme provider around the
parent would not automatically style separately mounted child widgets.

## Frontend behavior

Each Astryx widget receives the synced `brand` trait and renders inside an
Astryx `Theme` provider. The frontend bridge:

1. Reads the widget `brand`.
2. Normalizes token names so they start with `--`.
3. Calls Astryx `defineTheme({name, tokens})`.
4. Wraps the rendered component in `<Theme theme={theme} mode={color_mode}>`.

If no brand tokens are provided, the widget uses the neutral Astryx theme.

