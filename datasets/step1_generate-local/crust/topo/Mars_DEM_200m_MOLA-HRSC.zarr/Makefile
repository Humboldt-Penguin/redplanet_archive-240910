# # TODO — read through this more thoroughly: https://tech.davis-hansson.com/p/make/
# SHELL := bash
# .ONESHELL:
# .SHELLFLAGS := -eu -o pipefail -c
# .DELETE_ON_ERROR:
# MAKEFLAGS += --warn-undefined-variables
# MAKEFLAGS += --no-builtin-rules

.PHONY: help dataset clean clean-final clean-raw


.DEFAULT_GOAL := help

help:
	@echo "Usage: 'make [TARGET]'."
	@echo ""
	@echo "[TARGET] options:"
	@echo "    [empty]        - Simply run 'make' (or 'make help') to see these instructions."
	@echo "    dataset        - Start docker container to reproduce dataset."
	@echo "    clean          - Delete 'data/' (all data files)."
	@echo "    clean-raw      - Delete 'data/raw/' (raw data files)."
	@echo "    clean-final    - Delete 'data/final/' (final data files)."


# TODO: just abandon the dumbass `docker compose` thing, it requires users to install something else, and it's introducing more dependencies/processes that are ultimately unnecessary/overcomplicated since i'm only ever building/running a single container (not to mention i don't even fully understand what docker compose up is doing in large part and what features it has)
dataset:
	mkdir -p data
	docker compose -f build/compose.yaml up --build 

clean:
	rm -rf data/

clean-final:
	rm -rf data/final/

clean-raw:
	rm -rf data/raw/