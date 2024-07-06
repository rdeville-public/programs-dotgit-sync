BUILD_DIR := ./dist

all: format lint test build

.PHONY: build
build:
	poetry export --without-hashes -o requirements.txt
	poetry config virtualenvs.create false
	poetry install
	poetry run pyinstaller \
		--clean \
		--noconfirm \
		--log-level WARN \
		--workpath /tmp \
		pyinstaller.spec
	poetry build
	nix build

test:
	poetry run coverage run -m pytest
	poetry run coverage json
	poetry run coverage-threshold --config .coverage-threshold.toml
	poetry run coverage report

coverage_html:
	poetry run coverage html
	firefox .coverage_html/index.html

format:
	poetry run ruff format

lint:
	poetry run ruff check

lint-fix:
	poetry run ruff check --fix

clean:
	rm -rf .*_cache .venv

veryclean: clean
	rm -rf dist requirements.txt
