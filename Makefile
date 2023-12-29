all: test

test:
	kalamine layouts/*.toml
	pytest

clean:
	rm -rf build
	rm -rf dist
	rm -rf include
	rm -rf kalamine.egg-info
	rm -rf kalamine/__pycache__

lint:
	flake8 kalamine

publish: test
	# flake8 kalamine
	rm -rf dist/*
	python3 -m build
	twine check dist/*
	twine upload dist/*

dev:
	# python3 -m pip install --user --upgrade twine wheel
	python3 -m pip install --user --upgrade build
	python3 -m pip install --user -e .
