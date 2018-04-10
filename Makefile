all:
	kalamine docs/samples/*.yaml

clean:
	rm -rf build
	rm -rf dist
	rm -rf include
	rm -rf kalamine.egg-info
	rm -rf kalamine/__pycache__

lint:
	flake8 kalamine

publish:
	#flake8 kalamine
	rm -rf dist/*
	python3 setup.py bdist_wheel
	python3 setup.py sdist
	twine upload dist/*

publish-deps:
	pip3 install --user twine wheel

dev:
	pip3 install --user -e .
