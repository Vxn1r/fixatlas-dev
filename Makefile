.PHONY: install test lint format-check validate build check

install:
	python -m pip install -e '.[dev]'

test:
	python -m pytest

lint:
	ruff check .

format-check:
	ruff format --check .

validate:
	fixatlas validate-registry src/fixatlas/data/rules.json

build:
	python -m build

check: test lint format-check validate
