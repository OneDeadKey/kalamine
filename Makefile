.PHONY: all dev test lint publish format clean

PYTHON3?=python3

all: format lint test

dev:  ## Install a development environment
	# $(PYTHON3) -m pip install --user --upgrade -e .[dev]
	uv pip install --upgrade -e .[dev]

format:  ## Format sources
	uv run ruff format kalamine
	uv run ruff check --fix kalamine

lint:  ## Lint sources
	uv run ruff format --check kalamine
	uv run ruff check kalamine
	uv run mypy kalamine

test:  ## Run tests
	# $(PYTHON3) -m kalamine.cli guide > docs/README.md
	# $(PYTHON3) -m kalamine.cli build layouts/*.toml
	# $(PYTHON3) -m pytest
	uv run kalamine guide > docs/README.md
	uv run kalamine build layouts/*.toml
	uv run pytest

publish: test  ## Publish package
	rm -rf dist
	# $(PYTHON3) -m build
	uv build
	uv run twine check dist/*
	uv run twine upload dist/*

clean:  ## Clean sources
	rm -rf build
	rm -rf dist
	rm -rf include
	rm -rf kalamine.egg-info
	rm -rf kalamine/__pycache__
