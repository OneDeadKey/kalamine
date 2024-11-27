.PHONY: all dev test lint publish format clean

PYTHON3?=python3

UV := $(shell command -v uv 2> /dev/null)

all: format lint test

dev:  ## Install a development environment
ifndef UV
	$(PYTHON3) -m pip install --user --upgrade -e .[dev]
else
	uv pip install --upgrade -e .[dev]
endif

format:  ## Format sources
ifndef UV
	ruff format kalamine
	ruff check --fix kalamine
else
	uv run ruff format kalamine
	uv run ruff check --fix kalamine
endif

lint:  ## Lint sources
ifndef UV
	ruff format --check kalamine
	ruff check kalamine
	mypy kalamine
else
	uv run ruff format --check kalamine
	uv run ruff check kalamine
	uv run mypy kalamine
endif

test:  ## Run tests
ifndef UV
	$(PYTHON3) -m kalamine.cli guide > docs/README.md
	$(PYTHON3) -m kalamine.cli build layouts/*.toml
	$(PYTHON3) -m pytest
else
	uv run kalamine guide > docs/README.md
	uv run kalamine build layouts/*.toml
	uv run pytest
endif

publish: test  ## Publish package
	rm -rf dist
ifndef UV
	$(PYTHON3) -m build
	twine check dist/*
	twine upload dist/*
else
	uv build
	uv run twine check dist/*
	uv run twine upload dist/*
endif

clean:  ## Clean sources
	rm -rf build
	rm -rf dist
	rm -rf include
	rm -rf kalamine.egg-info
	rm -rf kalamine/__pycache__
