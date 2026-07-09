DOCS_PORT ?= 4200
DOCS_HOST ?= 127.0.0.1
OPEN ?= open
DOCS_URL = http://$(DOCS_HOST):$(DOCS_PORT)/

.PHONY: install-dev
install-dev:
	uv sync --group dev
	npm ci
	npm run build
	uv run --no-sync jupytext-config set-default-viewer

.PHONY: frontend
frontend:
	npm run build

.PHONY: test
test:
	uv run pytest

.PHONY: docs-reference
docs-reference:
	uv run --no-sync quartodoc build --config web/_quarto.yml
	uv run --no-sync python scripts/patch_reference_signatures.py

.PHONY: docs-clean-output
docs-clean-output:
	rm -rf web/_site
	find web -name '*.html' -not -path 'web/_site/*' -delete

.PHONY: docs-check-port
docs-check-port:
	@if lsof -nP -iTCP:$(DOCS_PORT) -sTCP:LISTEN >/dev/null 2>&1; then \
		echo "Port $(DOCS_PORT) is already in use. Stop the process below or run with DOCS_PORT=<free-port>:"; \
		lsof -nP -iTCP:$(DOCS_PORT) -sTCP:LISTEN; \
		exit 1; \
	fi

.PHONY: docs
docs: docs-reference docs-clean-output
	quarto render web

.PHONY: docs-preview
docs-preview: docs-reference docs-clean-output
	(sleep 2; $(OPEN) $(DOCS_URL)) &
	quarto preview web --no-browser --port $(DOCS_PORT)

.PHONY: docs-serve
docs-serve: docs-check-port docs
	(sleep 1; $(OPEN) $(DOCS_URL)) &
	uv run --no-sync python -m http.server $(DOCS_PORT) --bind $(DOCS_HOST) --directory web/_site
