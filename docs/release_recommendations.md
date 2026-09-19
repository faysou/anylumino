# Release Recommendations

Prepare the first public release as an alpha. The package builds and the examples
run in JupyterLab. License packaging, the copyright holder, and the supported
Python version are settled; saved widget-state size and browser coverage remain
open.

## License packaging

`THIRD_PARTY_LICENSES.md` inventories every package that the frontend build
compiles into `src/anylumino/static`, with the upstream notice text for each one.
`npm run licenses` regenerates it from the esbuild inputs, so documentation-site
dependencies stay out of the runtime inventory, and CI fails when the committed
file falls behind. Packages that publish no license file, currently Lumino,
Astryx, and StyleX, take their notice from `licenses/`; the generator fails on a
new package that has neither.

`pyproject.toml` ships both `LICENSE` and `THIRD_PARTY_LICENSES.md` through
`license-files`, so the wheel carries the notices it needs. The copyright holder
and author are Faysal Aberkane.

## Reduce saved widget-state size

Each anywidget model carries its own `_esm` and `_css` state, so a saved notebook
repeats the bundle once per widget instance. Converting the Jupytext examples to
`.ipynb` and executing them with widget state saved produced a 124.9 MB component
smoke notebook and a 74.6 MB theme notebook, the former holding 112 copies of the
same approximately 919 KB JavaScript bundle and 152 KB stylesheet. Those files
were local conversions and are not in the repository, which tracks only the
Jupytext `.py` sources, but any user who saves a notebook with widget state hits
the same cost.

Investigate sharing frontend assets between widget models while preserving
offline operation. Check notebook size, reopening behavior, and interactive
rendering before changing the asset-loading mechanism.

Document how to omit saved widget state for notebooks that will be rerun with a
kernel. For automated execution, nbconvert supports
`--ExecutePreprocessor.store_widget_state=False`. Such outputs do not retain the
widget state needed to restore an interactive view without rerunning the cells.
Keep the Jupytext source examples free of saved outputs.

## Define supported environments

`pyproject.toml` requires Python 3.14 and later, which matches the single CI
lane. Adding an older interpreter back means adding its CI lane in the same
change.

Document the supported notebook hosts and browsers. The visual checks cover
JupyterLab in Chromium on macOS; they do not establish compatibility with Safari,
Firefox, VS Code notebooks, or static notebook exports. Prioritize browser checks
for nested layouts, popup positioning, keyboard input, and theme changes.

Keep the Python regression tests, frontend tests, distribution build, and
installed-wheel check in CI. Add browser smoke coverage for rendering, selection,
slider updates, and resizing. Give the repository its own lint configuration;
inherited workspace rules and a generic Markdown checker produce existing
diagnostics that do not match the generated MDX documentation.

## Prepare the public documentation

Provide installation instructions that distinguish using the package from
building its frontend and documentation. Explain how to open the Jupytext
examples and which optional dependencies each example needs.

Add a changelog, contribution guidance, and a clear policy for API changes during
the alpha period. Document row-ID uniqueness, keyed child ownership, callbacks,
and the distinction between live widgets and saved notebook output. Use a small
gallery of screenshots alongside runnable examples.

## Rehearse publication

Build the wheel and source archive from the release revision with `uv build`.
Inspect both artifacts, then install the wheel in a clean environment outside the
checkout with `uv venv` and `uv pip install`. Run an example using that
installation to verify that the frontend assets are present.

Publish a prerelease to [TestPyPI](https://packaging.python.org/en/latest/guides/using-testpypi/)
with `uv publish --publish-url https://test.pypi.org/legacy/`, then create a
fresh environment and install the published package from TestPyPI with
`uv pip install --index-url https://test.pypi.org/simple/`. Verify the installed
version and run an example before publishing to PyPI with `uv publish`.
Configure [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
for the release workflow. Confirm repository visibility, project links, the
version, and the license inventory before the public release.

## Local release checklist

Run the following commands from a clean release checkout:

```sh
npm ci
npm run build
uv sync --group dev
uv run --no-sync pytest
make docs-check
uv build
uv publish --dry-run --trusted-publishing never dist/*
```

Create the clean wheel environment outside the checkout and run the installed
package smoke check before publishing:

```sh
uv venv /tmp/anylumino-wheel
uv pip install --python /tmp/anylumino-wheel/bin/python dist/*.whl
```

The package requires Python 3.14 and later, as declared in `pyproject.toml`, and
CI tests that single lane on Ubuntu.
Browser validation currently covers Chromium-based JupyterLab; Safari, Firefox,
VS Code notebooks, and static exports require separate checks before claiming
support.
