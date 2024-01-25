.PHONY: all dev test lint publish format clean

all: test

dev:  ## Install a development environment
	# python3 -m pip install --user --upgrade twine wheel
	python3 -m pip install --user --upgrade build
	python3 -m pip install --user -e .


test:  ## Run tests
	# python3 -m kalamine.cli make layouts/*.toml
	kalamine make layouts/*.toml
	pytest

publish: test  ## Publish package
	# flake8 kalamine
	rm -rf dist/*
	python3 -m build
	twine check dist/*
	twine upload dist/*

lint:  ## Lint sources
	flake8 kalamine

format:  ## Format sources
	isort .
	black .

clean:  ## Clean sources
	rm -rf build
	rm -rf dist
	rm -rf include
	rm -rf kalamine.egg-info
	rm -rf kalamine/__pycache__
