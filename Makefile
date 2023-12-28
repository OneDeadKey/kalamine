all:
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

publish:
	# flake8 kalamine
	rm -rf dist/*
	python3 -m build
	# python3 setup.py bdist_wheel
	# python3 setup.py sdist
	twine check dist/*
	twine upload dist/*

dev:
	python3 -m pip install --user --upgrade build
	python3 -m pip install --user -e .
