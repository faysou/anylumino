# Astryx theme wrappers

`AstryxBrand`, `AstryxBuiltTheme`, and `AstryxTheme` provide reusable ways to
apply Astryx theme identity to notebook widgets without passing style-related
props to each component. The frontend bridge uses Astryx `Theme`; runtime
themes are created with `defineTheme()`, while precompiled themes use CSS from
`npx astryx theme build`. See the upstream theme docs at
<https://astryx.atmeta.com/themes>.

## AstryxBrand

`AstryxBrand` creates a JSON-safe Astryx `defineTheme()` token record that can
be synced to the frontend.

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
        "--color-accent": ["#0057b8", "#79b8ff"],
        "--color-background-card": ["#ffffff", "#111827"],
        "--color-text-primary": ["#111827", "#f9fafb"],
        "--radius-container": "8px",
    },
}
```

Token names may include or omit the CSS custom property prefix. The Python API
normalizes `color-accent` to `--color-accent` before syncing the token record.

Token values can be strings or two-item light/dark tuples. For example,
`("white", "black")` becomes a mode-aware token value.

## AstryxBuiltTheme

`AstryxBuiltTheme` describes a precompiled Astryx theme. Use it when a theme has
already been built to CSS with the Astryx CLI.

```python
built_theme = al.AstryxBuiltTheme(
    "trading-desk",
    css="themes/trading-desk/theme.css",
    tokens={
        "color-accent": "#0057b8",
        "radius-container": "8px",
    },
)
```

The `name` must match the `name` in the TypeScript theme source because the
generated CSS is scoped by `data-astryx-theme="<name>"`. The `css` argument can
be CSS text or a path-like object. Pass `css=None` for a built theme whose CSS
is already bundled by AnyLumino, such as the default neutral theme.

The optional `tokens` mapping is retained in the synced theme object for Astryx
hooks and debugging. The generated CSS is what actually styles the widgets.

## AstryxTheme

`AstryxTheme` applies a runtime or precompiled theme and color mode to a subtree
of Astryx widgets. It renders as an Astryx `Stack`, so it also accepts layout
options such as `direction` and `gap`.

```python
app = al.AstryxTheme(
    {
        "header": header,
        "controls": controls,
        "table": table,
    },
    brand=brand,
    mode="system",
    gap=3,
)
```

Use `mode="light"`, `mode="dark"`, or `mode="system"`. `color_mode` remains
available as the Python trait name, but `mode` matches the Astryx `Theme` prop
and takes precedence when provided.

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
mounted in its own frontend root. A normal React `Theme` provider around the
parent would not automatically style separately mounted child widgets.

## Defining a new precompiled theme

Create a TypeScript theme file using Astryx `defineTheme()`:

```ts
// themes/tradingDeskTheme.ts
import {defineTheme} from '@astryxdesign/core/theme';

export const tradingDeskTheme = defineTheme({
  name: 'trading-desk',
  color: {accent: '#0057b8', neutralStyle: 'cool'},
  radius: {base: 4, multiplier: 1},
  tokens: {
    '--color-background-card': ['#ffffff', '#111827'],
    '--color-text-primary': ['#111827', '#f9fafb'],
  },
});
```

Build the CSS artifact:

```sh
npm run astryx -- theme build themes/tradingDeskTheme.ts --out themes/trading-desk/theme.css
```

Use the generated CSS from Python:

```python
theme = al.AstryxBuiltTheme(
    "trading-desk",
    css=Path("themes/trading-desk/theme.css"),
)

panel = al.AstryxTheme([al.AstryxButton("Refresh")], brand=theme, mode="system")
```

Use this path when a theme includes generated component overrides, scale
configuration, or enough CSS that runtime injection is no longer desirable.
Use `AstryxBrand` for small notebook-local token overrides.

## Frontend behavior

Each Astryx widget receives the synced `brand` trait and renders inside an
Astryx `Theme` provider. The frontend bridge:

1. Reads the widget `brand`.
2. For runtime brands, calls Astryx `defineTheme({name, tokens})`.
3. For built themes, injects supplied generated CSS once per unique theme/CSS
   pair and passes a `__built` theme object to Astryx.
4. Wraps the rendered component in `<Theme theme={theme} mode={color_mode}>`.

If no brand tokens are provided, the widget uses the neutral Astryx theme.
Custom icon registries are not serialized from Python because Astryx icon
registries contain React components/functions. Bundle custom icons on the
frontend side if a theme depends on them.

## How notebook rendering works

The Python wrappers synchronize plain JSON over traitlets. `AstryxBrand`
returns a runtime descriptor with a `name` and `tokens`. `AstryxBuiltTheme`
returns a built descriptor with `name`, `built=True`, generated `css`, optional
`tokens`, and optional `components`. `AstryxTheme` stores that descriptor on
itself and applies the same descriptor and color mode to every nested Astryx
widget before display.

That explicit propagation is important in JupyterLab. A notebook output can
contain several anywidget roots, and nested AnyLumino children are mounted by
the widget manager as separate React roots. A React context provider around the
parent output would not automatically reach those separate roots, so the theme
identity is synchronized on each child model instead.

Runtime brands are converted in the browser with Astryx `defineTheme()`.
Precompiled themes are different: the generated CSS is inserted into
`document.head` using a `data-anylumino-astryx-built-theme-id` attribute based
on the theme name and CSS hash. Multiple notebook outputs using the same built
theme share one style element. The bridge increments
`data-anylumino-astryx-built-theme-count` for each mounted user and removes the
style element after the last themed output unmounts.

This DOM-level deduplication is deliberate. JupyterLab and anywidget can load
the same bundled frontend module more than once across notebooks, workspaces,
or development reloads. A module-local JavaScript cache would not be reliable
in that environment, while a `document.head` lookup is shared by all widget
roots in the page.

## Testing in JupyterLab

Use the theme smoke notebook when changing theme behavior:

```sh
uv run --no-sync jupytext \
  --to ipynb \
  --execute notebooks/astryx_themes.py \
  --output - >/tmp/astryx_themes.ipynb
```

For browser validation, rebuild the frontend bundle before starting JupyterLab:

```sh
npm run build
uv run --no-sync jupyter lab . --port=8888 --no-browser --ServerApp.token='' --ServerApp.password=''
```

Then open `notebooks/astryx_themes.py`, run all cells, and inspect the rendered
outputs. A correct run shows the runtime light, runtime dark, runtime system,
and built system panels. In the browser DOM, repeated uses of the same built
theme should produce one `style[data-anylumino-astryx-built-theme-id]` element
with a reference count rather than one duplicate style element per output.

During frontend development, restart the Jupyter server and use a fresh browser
task space or clear the browser cache after rebuilding. JupyterLab can otherwise
reuse an older ES module instance for an anywidget bundle even after the file on
disk has changed, which makes style-injection tests appear stale.
