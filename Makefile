.PHONY: all dev test lint publish format clean

all: format lint test

dev:  ## Install a development environment
	python3 -m pip install --user --upgrade .[dev]
	# python3 -m pip install --user --upgrade build
	# python3 -m pip install --user --upgrade twine wheel

format:  ## Format sources
	black kalamine
	isort kalamine

lint:  ## Lint sources
	black --check --quiet kalamine
	isort --check --quiet kalamine
	ruff kalamine
	mypy kalamine

test:  ## Run tests
	python3 -m kalamine.cli guide > docs/README.md
	python3 -m kalamine.cli build layouts/*.toml
	pytest

publish: test  ## Publish package
	rm -rf dist/*
	python3 -m build
	twine check dist/*
	twine upload dist/*

clean:  ## Clean sources
	rm -rf build
	rm -rf dist
	rm -rf include
	rm -rf kalamine.egg-info
	rm -rf kalamine/__pycache__
