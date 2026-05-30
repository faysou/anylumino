UV ?= uv
UV_CACHE_DIR ?= .uv-cache

.PHONY: install-dev
install-dev:
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) sync --group dev
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run --no-sync jupytext-config set-default-viewer

.PHONY: lab
lab:
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run --no-sync jupyter lab

.PHONY: test
test:
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run pytest
