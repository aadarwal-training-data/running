.PHONY: sync test lint notebook-check check notebooks paper clean

sync:
	uv sync --dev

test:
	uv run pytest

lint:
	uv run ruff check src tests notebooks

notebook-check:
	uv run marimo check --strict notebooks/*.py

check: lint notebook-check test

notebooks:
	mkdir -p html
	@for notebook in notebooks/*.py; do \
		name=$$(basename "$$notebook" .py); \
		uv run marimo export html "$$notebook" --no-include-code -o "html/$$name.html" -f; \
	done

paper:
	mkdir -p build
	cd tex && tectonic -X compile main.tex --outdir ../build
	cp build/main.pdf tex/cryptograph-theory.pdf

clean:
	rm -rf build html .pytest_cache .ruff_cache
