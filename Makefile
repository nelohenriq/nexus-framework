# NEXUS Framework - Makefile
.PHONY: install test lint format clean run demo docs help

help:
	@echo "NEXUS Framework - Available commands:"
	@echo " make install Install dependencies"
	@echo " make test Run all tests"
	@echo " make lint Check code quality"
	@echo " make format Format code with black"
	@echo " make clean Clean build artifacts"
	@echo " make run Run NEXUS CLI"
	@echo " make demo Run demo script"
	@echo " make docs Build documentation"

install:
	pip install -e "."
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=nexus --cov-report=html

lint:
	ruff check nexus/
	mypy nexus/

format:
	black nexus/
	isort nexus/

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +

run:
	python -m nexus.cli.main

demo:
	python nexus_demo.py

docs:
	cd docs && mkdocs serve

api:
	uvicorn nexus.api.rest:app --reload --port 8000