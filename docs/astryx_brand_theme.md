# Astryx theme wrappers

`Brand`, `BuiltTheme`, and `Theme` provide reusable ways to
apply Astryx theme identity to notebook widgets without passing style-related
props to each component. The frontend bridge uses Astryx `Theme`; runtime
themes are created with `defineTheme()`, while precompiled themes use CSS from
`npx astryx theme build`. See the upstream theme docs at
<https://astryx.atmeta.com/themes>.

## Brand

`Brand` creates a JSON-safe Astryx `defineTheme()` token record that can
be synced to the frontend.

```python
import anylumino as al
import anylumino.astryx as ax

brand = ax.Brand(
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

## BuiltTheme

`BuiltTheme` describes a precompiled Astryx theme. Use it when a theme has
already been built to CSS with the Astryx CLI.

```python
built_theme = ax.BuiltTheme(
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

## Theme

`Theme` applies a runtime or precompiled theme and color mode to a subtree
of Astryx widgets. It renders as an Astryx `Stack`, so it also accepts layout
options such as `direction` and `gap`.

```python
app = ax.Theme(
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
`Widget` children:

```python
button = ax.Button("Refresh")
panel = ax.Theme([button], brand=brand, color_mode="dark")

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
theme = ax.BuiltTheme(
    "trading-desk",
    css=Path("themes/trading-desk/theme.css"),
)

panel = ax.Theme([ax.Button("Refresh")], brand=theme, mode="system")
```

Use this path when a theme includes generated component overrides, scale
configuration, or enough CSS that runtime injection is no longer desirable.
Use `Brand` for small notebook-local token overrides.

## Frontend behavior

Each Astryx widget receives the synced `brand` trait and renders inside an
Astryx `Theme` provider. The frontend bridge:

1. Reads the widget `brand`.
2. For runtime brands, calls Astryx `defineTheme({name, tokens})` and generates
   the theme CSS with Astryx `generateThemeCSS()`.
3. For built themes, uses the supplied generated CSS.
4. Injects that CSS once per unique theme/CSS pair, reference counted, and
   passes a `__built` theme object to Astryx so Astryx skips its own injection.
5. Resolves `color_mode` and wraps the rendered component in
   `<Theme theme={theme} mode={resolved_mode}>`.

If no brand tokens are provided, the widget uses the neutral Astryx theme.
Custom icon registries are not serialized from Python because Astryx icon
registries contain React components/functions. Bundle custom icons on the
frontend side if a theme depends on them.

## How notebook rendering works

The Python wrappers synchronize plain JSON over traitlets. `Brand`
returns a runtime descriptor with a `name` and `tokens`. `BuiltTheme`
returns a built descriptor with `name`, `built=True`, generated `css`, optional
`tokens`, and optional `components`. `Theme` stores that descriptor on
itself and applies the same descriptor and color mode to every nested Astryx
widget before display.

That explicit propagation is important in JupyterLab. A notebook output can
contain several anywidget roots, and nested AnyLumino children are mounted by
the widget manager as separate React roots. A React context provider around the
parent output would not automatically reach those separate roots, so the theme
identity is synchronized on each child model instead.

Runtime brands are converted in the browser with Astryx `defineTheme()`.
anylumino then marks the result `__built` and injects the CSS itself, on the
same path as precompiled themes: the CSS is inserted into `document.head` using
a `data-anylumino-astryx-theme-id` attribute based on the theme name and CSS
hash. Multiple notebook outputs using the same theme share one style element.
The bridge increments `data-anylumino-astryx-theme-count` for each mounted user
and removes the style element after the last themed output unmounts.

Owning the injection matters because Astryx dedupes runtime themes by name in a
module-level set and drops the shared style tag when the first injecting widget
unmounts. In a notebook, closing one output would then strip brand tokens from
every output that remains.

This DOM-level deduplication is deliberate. JupyterLab and anywidget can load
the same bundled frontend module more than once across notebooks, workspaces,
or development reloads. A module-local JavaScript cache would not be reliable
in that environment, while a `document.head` lookup is shared by all widget
roots in the page.

## Color modes and the host page

`color_mode` accepts `"light"`, `"dark"`, `"system"`, and `"jupyterlab"`.
`"system"` follows the OS `prefers-color-scheme`. `"jupyterlab"` resolves to
light or dark from `body[data-jp-theme-light]` and follows later theme changes
through one shared `MutationObserver`.

An Astryx `Theme` with no parent `Theme` syncs `html[data-theme]` to the
document so browser chrome matches the mode. Every anywidget is its own React
root, so in a notebook every widget is a root theme: the last output to mount
decides the page attribute, and the first to unmount clears it even though other
outputs are still on screen.

anylumino records the value the host page had before any Astryx widget mounted
and restores it once the last Astryx widget unmounts, so clearing one output does
not leave the page with no mode. While widgets are mounted the upstream
last-mount-wins behavior stands: a widget with `mode="dark"` does set the page
attribute.

Correcting each write instead is not viable. Writing to `html` invalidates style
for the whole document, so reverting every write from a `MutationObserver` turns
into a style-recalc war with Astryx's own layout effect. In a notebook with a
hundred widgets that measured as thousands of full-document style recalculations
and paints, which stalls the browser for long enough to look like a hang.

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
runtime JupyterLab, built system, and built JupyterLab panels. Toggle the
JupyterLab theme and confirm the two JupyterLab panels follow it while the
others do not, and that the surrounding notebook chrome never changes with a
dark panel on screen. In the browser DOM, repeated uses of the same theme should
produce one `style[data-anylumino-astryx-theme-id]` element with a reference
count rather than one duplicate style element per output.

During frontend development, restart the Jupyter server and use a fresh browser
task space or clear the browser cache after rebuilding. JupyterLab can otherwise
reuse an older ES module instance for an anywidget bundle even after the file on
disk has changed, which makes style-injection tests appear stale.
