# NOTE / TODO / WARNING — I made this to learn/practice makefiles for the first time. I've NEVER tested ANY of these commands, nor do I even think they'd always work on Windows (`make` is installed via choco, but commands like `clean` are written with unix-syntax). When doing real tests, be ESPECIALLY careful with `publish`, `build`, and `clean` (make a commit and physical backup) !!!
# TODO — Keep in mind that many/most/all of the people looking at your code may not know what a Makefile even is!! Don't just assume "advanced users who want to edit my code will either know this, or be willing to figure it out", because I want to ENCOURAGE/INVITE people and make it as accessible as possible to contribute!!! Recall how I was deterred from anything `make`-related since I was averse to C, but when I learned more (especially the more generalized idea that Makefiles are just shortcut scripts) I thought they were really cool!!! ——— THEREFORE, at the top of this file, make a basic readme/explanation of what a Makefile is, how it works, and how to use it (esp if you're on Windows). I can even link a ChatGPT explanation lmao, if it gets more extensive then probs make a separate markdown file in docs and link to it. 


# # TODO — read through this more thoroughly: https://tech.davis-hansson.com/p/make/
# SHELL := bash
# .ONESHELL:
# .SHELLFLAGS := -eu -o pipefail -c
# .DELETE_ON_ERROR:
# MAKEFLAGS += --warn-undefined-variables
# MAKEFLAGS += --no-builtin-rules







.PHONY: help install install-dev publish build clean


.DEFAULT_GOAL := help

help:
	@echo "Usage: 'make [TARGET]'."
	@echo ""
	@echo "[TARGET] options:"
	@echo "    [empty]        - Simply run 'make' (or 'make help') to see these instructions."
	@echo "    install        - Pip-install the package in the active Python environment."
	@echo "    install-dev    - Same as 'install', but modifications to source code are immediately effective, and you have tools to 'build' and 'publish' to PyPI."
	@echo "    publish        - 'clean', 'build', then publish the package to PyPI."
	@echo "    build          - 'clean', then build the package."
	@echo "    clean          - Clean up build artifacts."


install:
	pip install .

install-dev:
	pip install -e ".[dev]"

publish: build
	twine upload dist/*
# TODO: should I update twine first...? (`python -m pip install --upgrade build`)

build: clean
	python -m build
# TODO: should I update build first...? (`python -m pip install --upgrade twine`)

clean:
	rm -rf dist/
	rm -rf src/redplanet.egg-info/
	rm -rf build/
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
