all:
	./bin/kalamine docs/samples/*.yaml

clean:
	rm -f dist/*

lint:
	flake8 kalamine
