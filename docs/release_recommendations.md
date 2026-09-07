# Release Recommendations

Prepare the first public release as an alpha. The package builds and the examples
run in JupyterLab, but license packaging, saved widget-state size, and supported
environments need explicit decisions before publication.

## Complete license packaging

The wheel includes bundled frontend dependencies. Its license directory contains
the project's MIT license, while some bundled comments refer to upstream license
files that are absent from the distribution.

Inventory the dependencies included by the frontend build and package their
required license texts and notices. Generate the inventory from the actual bundle
inputs so documentation-site dependencies do not get mixed into the runtime
inventory. Confirm that `Nautilus` is the intended copyright holder in `LICENSE`
and author name in `pyproject.toml`.

## Reduce saved widget-state size

The September 2026 notebook checks produced a 124.9 MB component smoke notebook
and a 74.6 MB theme notebook when widget state was saved. The component notebook
contained 112 copies of the same approximately 919 KB JavaScript bundle and
152 KB stylesheet. This makes notebook sharing and reopening costly even though
the compressed wheel is small.

Investigate sharing frontend assets between widget models while preserving
offline operation. Check notebook size, reopening behavior, and interactive
rendering before changing the asset-loading mechanism.

Document how to omit saved widget state for notebooks that will be rerun with a
kernel. For automated execution, nbconvert supports
`--ExecutePreprocessor.store_widget_state=False`. Such outputs do not retain the
widget state needed to restore an interactive view without rerunning the cells.
Keep the Jupytext source examples free of saved outputs.

## Define supported environments

CI targets Python 3.14, while package metadata permits Python 3.10 and later.
Decide whether the older versions remain a support promise. Either verify that
promise separately or deliberately raise the minimum Python version.

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

Build the wheel and source archive from the release revision, run
`twine check --strict`, and install the wheel in a clean environment outside the
checkout. Run an example using that installation to verify that frontend assets
are present.

Publish a prerelease to [TestPyPI](https://packaging.python.org/en/latest/guides/using-testpypi/)
and verify installation before uploading to PyPI. Configure
[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
for the release workflow. Confirm repository visibility, project links, the
version, and the license inventory before the public release.
