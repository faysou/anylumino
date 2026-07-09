UV ?= uv
UV_CACHE_DIR ?= .uv-cache
LAB_PORT ?= 8888
DOCS_PORT ?= 4200
OPEN ?= open
DOCS_URL = http://127.0.0.1:$(DOCS_PORT)/

.PHONY: install-dev
install-dev:
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) sync --group dev
	npm ci
	npm run build
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run --no-sync jupytext-config set-default-viewer

.PHONY: frontend
frontend:
	npm run build

.PHONY: lab
lab:
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run --group dev jupyter lab . --port=$(LAB_PORT)

.PHONY: test
test:
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run pytest

.PHONY: docs-reference
docs-reference:
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run --no-sync quartodoc build --config web/_quarto.yml
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run --no-sync python scripts/patch_reference_signatures.py

.PHONY: docs-clean-output
docs-clean-output:
	rm -rf web/_site
	find web -name '*.html' -not -path 'web/_site/*' -delete

.PHONY: docs
docs: docs-reference docs-clean-output
	quarto render web

.PHONY: docs-preview
docs-preview: docs-reference docs-clean-output
	(sleep 2; $(OPEN) $(DOCS_URL)) &
	quarto preview web --no-browser --port $(DOCS_PORT)

.PHONY: docs-serve
docs-serve: docs
	(sleep 1; $(OPEN) $(DOCS_URL)) &
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run --no-sync python -m http.server $(DOCS_PORT) --directory web/_site
