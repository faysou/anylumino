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
current by running `npm run build` after frontend changes.

Keep pull requests focused. Add or update a runnable notebook when a change
introduces a user-facing widget pattern, and update the relevant documentation
when public behavior changes.
