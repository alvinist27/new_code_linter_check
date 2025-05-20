.DEFAULT_GOAL := all
.PHONY: all lint tests

all:  # Run all checks
	make lint
	make tests

lint:  ## Run lint and static-check code
	./linter/run_analyze.sh

tests:  ## Run project tests
	pytest --alluredir allure-results
