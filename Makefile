.PHONY: dev lint type-check test build demo clean

dev:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/

type-check:
	mypy src/ --strict

test:
	pytest tests/ -v --cov=src/churnmap --cov-report=term-missing

build:
	python -m build

demo:
	churnmap --repo . --output-dir /tmp/churnmap-demo --min-occurrences 1 --open

clean:
	rm -rf dist/ build/ *.egg-info/ src/*.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/ .coverage coverage.xml htmlcov/
