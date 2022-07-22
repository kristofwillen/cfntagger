.PHONY: test build

all: clean test build

test:
	pipenv run pytest -vv

build:
	/usr/bin/env python3 ./setup.py bdist_wheel

upload:
	twine upload dist/*

clean:
	rm dist/*
