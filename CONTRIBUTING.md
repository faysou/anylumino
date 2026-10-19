# Contributing

Install the development dependencies and build the frontend before running the
checks:

```sh
uv sync --group dev
npm ci
npm run build
```

Run `uv run --no-sync pytest` for Python tests, `npm test` for frontend tests,
and `make docs-check` for generated API pages, documentation links, linting,
types, and the production documentation build. Keep generated frontend bundles
current by running `npm run build` after frontend changes, and regenerate
`THIRD_PARTY_LICENSES.md` with `npm run licenses` after frontend dependency
changes. CI verifies both files.

To test against a local anywidget checkout in `../anywidget`, run
`make install-dev-anywidget-local`. It builds the checkout's frontend with
`pnpm` and installs the checkout as an editable package into the anylumino
environment. `pyproject.toml` and `uv.lock` stay unchanged, so use
`uv run --no-sync` afterwards: a plain `uv run` or `uv sync` reinstalls
anywidget from PyPI. Run the target again after frontend changes in the
checkout, and set `ANYWIDGET_LOCAL` to use another path.

Keep pull requests focused. Add or update a runnable notebook when a change
introduces a user-facing widget pattern, and update the relevant documentation
when public behavior changes.

Releases run from a `v*` tag. Bump the version in `pyproject.toml`, tag the
release commit, and push the tag; the Release workflow builds the
distributions, attaches them to the GitHub release, and publishes to PyPI
through Trusted Publishing.
