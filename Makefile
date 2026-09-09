.PHONY: install format lint test-build test build

install:
	python3 -m venv .venv
	.venv/bin/pip install -e '.[dev]' pytest pytest-django ruff build

format:
	.venv/bin/ruff format django_hashstore tests

lint:
	.venv/bin/ruff check

# Python has no separate compile step for a library this size; the closest
# equivalent is asking the interpreter to byte-compile every module.
test-build:
	.venv/bin/python3 -m compileall -q django_hashstore tests

test:
	.venv/bin/pytest

build:
	.venv/bin/python3 -m build
