DOCS_PORT ?= 4200
DOCS_HOST ?= 127.0.0.1
OPEN ?= open
DOCS_URL = http://$(DOCS_HOST):$(DOCS_PORT)/docs

.PHONY: install-dev
install-dev:
	uv sync --group dev
	# JupyterLab runs CommonJS scripts from site-packages; without this file Node
	# applies the repo's "type": "module" to them and they fail at startup.
	printf '{"type": "commonjs"}\n' > .venv/package.json
	npm ci
	npm run build
	uv run --no-sync jupytext-config set-default-viewer

ANYWIDGET_LOCAL ?= ../anywidget

.PHONY: install-dev-anywidget-local
install-dev-anywidget-local:
	pnpm --dir $(ANYWIDGET_LOCAL) install --frozen-lockfile
	pnpm --dir $(ANYWIDGET_LOCAL) build
	pnpm --dir $(ANYWIDGET_LOCAL) --filter anywidget build
	uv pip install --reinstall-package anywidget -e $(ANYWIDGET_LOCAL)
	@echo "anywidget now comes from $(ANYWIDGET_LOCAL). Use 'uv run --no-sync' for later commands;"
	@echo "a plain 'uv run' or 'uv sync' restores PyPI anywidget from uv.lock."

.PHONY: update-dependencies
update-dependencies:
	uv lock \
		--upgrade-package anywidget \
		--upgrade-package jupyter \
		--upgrade-package jupyterlab \
		--upgrade-package jupyter-builder
	npm install --save-exact @lumino/commands@latest @lumino/widgets@latest
	npm install --save-prefix='^' @astryxdesign/core@latest @astryxdesign/theme-neutral@latest
	npm install --save-dev --save-prefix='^' @astryxdesign/cli@latest
	npm run build

.PHONY: frontend
frontend:
	npm run build

.PHONY: workbench-skill
workbench-skill:
	uv run --no-sync python -c "from anylumino.workbench import skill; skill.write()"

.PHONY: test
test:
	npm test
	uv run pytest

.PHONY: docs-reference
docs-reference: docs-install
	@mkdir -p build/docs
	PYTHONPATH=node_modules/fumadocs-python:src uv run --no-sync python -c 'from fumapy import generate; generate()' anylumino --docstring-style numpy --dir build/docs
	npm run docs:convert
	uv run --no-sync python scripts/docs_examples.py api-images

.PHONY: docs-install
docs-install:
	uv sync --group dev
	npm ci

.PHONY: docs-check-port
docs-check-port:
	@if lsof -nP -iTCP:$(DOCS_PORT) -sTCP:LISTEN >/dev/null 2>&1; then \
		echo "Port $(DOCS_PORT) is already in use. Stop the process below or run with DOCS_PORT=<free-port>:"; \
		lsof -nP -iTCP:$(DOCS_PORT) -sTCP:LISTEN; \
		exit 1; \
	fi

.PHONY: docs
docs: docs-reference
	npm run docs:build

.PHONY: docs-preview
docs-preview: docs-reference
	(sleep 2; $(OPEN) $(DOCS_URL)) &
	npm run docs:dev -- --hostname $(DOCS_HOST) --port $(DOCS_PORT)

.PHONY: docs-serve
docs-serve: docs-check-port docs
	(sleep 1; $(OPEN) $(DOCS_URL)) &
	uv run --no-sync python -m http.server $(DOCS_PORT) --bind $(DOCS_HOST) --directory out

.PHONY: docs-check
docs-check: docs-reference
	npm run docs:test-links
	npm run docs:lint
	npm run docs:types
	npm run docs:build

# Capture the documentation screenshots. The capture starts its own JupyterLab
# and runs headless Chromium; install it once with
# `uv run --no-sync playwright install chromium`.
.PHONY: docs-screenshots
docs-screenshots:
	uv run --no-sync python scripts/docs_examples.py capture docs
	uv run --no-sync python scripts/docs_examples.py images

.PHONY: docs-screenshots-components
docs-screenshots-components:
	uv run --no-sync python scripts/docs_examples.py capture components
