.PHONY: test

GITFILES=$(shell git ls-files '*.py')

all: clean test build

test:
	pipenv run pytest -vv

lint:
	pylint $(GITFILES)

build:
	/usr/bin/env python3 ./setup.py bdist_wheel

upload:
	twine upload dist/*

clean:
	rm dist/*
