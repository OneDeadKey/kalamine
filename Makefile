.PHONY: all dev test lint publish format clean

PYTHON3?=python3

all: format lint test

dev:  ## Install a development environment
	$(PYTHON3) -m pip install --user --upgrade -e .[dev]
	# $(PYTHON3) -m pip install --user --upgrade build
	# $(PYTHON3) -m pip install --user --upgrade twine wheel

format:  ## Format sources
	black kalamine
	isort kalamine

lint:  ## Lint sources
	black --check --quiet kalamine
	isort --check --quiet kalamine
	ruff check kalamine
	mypy kalamine

test:  ## Run tests
	$(PYTHON3) -m kalamine.cli guide > docs/README.md
	$(PYTHON3) -m kalamine.cli build layouts/*.toml
	$(PYTHON3) -m pytest

publish: test  ## Publish package
	rm -rf dist/*
	$(PYTHON3) -m build
	twine check dist/*
	twine upload dist/*

clean:  ## Clean sources
	rm -rf build
	rm -rf dist
	rm -rf include
	rm -rf kalamine.egg-info
	rm -rf kalamine/__pycache__
