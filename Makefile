# Makefile for tests
ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

VENV := test_venv
VENV_BIN := $(VENV)/bin

# simulate running in headless mode
unexport DISPLAY

# Test coverage pass threshold (percent)
MIN_COV ?= 90

FIND_LINT_PY=`find tns -name "*.py" -not -path "*/*test*"`
LINT_PYFILES := $(shell find $(FIND_LINT_PY))

$(VENV):
	virtualenv --system-site-packages $(VENV)
	$(VENV_BIN)/pip install --ignore-installed -r requirements_dev.txt
	$(VENV_BIN)/pip install -e .

run_pep8: $(VENV)
	$(VENV_BIN)/pep8 --config=pep8rc $(LINT_PYFILES) > pep8.txt

run_pylint: $(VENV)
	$(VENV_BIN)/pylint --rcfile=pylintrc --extension-pkg-whitelist=numpy $(LINT_PYFILES) > pylint.txt

run_tests: $(VENV)
	$(VENV_BIN)/nosetests -v --with-coverage --cover-min-percentage=$(MIN_COV) --cover-package tns

lint: run_pep8 run_pylint

test: lint run_tests

clean_test_venv:
	@rm -rf $(VENV)
	@rm -rf $(ROOT_DIR)/test-reports

clean: clean_test_venv
	@rm -f pep8.txt
	@rm -f pylint.txt
	@rm -rf tns.egg-info
	@rm -f .coverage
	@rm -rf test-reports
	@rm -rf dist
	@pyclean tns

.PHONY: run_pep8 run_pylint test
