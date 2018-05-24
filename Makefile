PYTHON?=python3
PYTHONPATH?=./
SOURCE_DIR=./avio
TESTS_DIR=./tests
BIN_DIR=./bin
TESTS_ARGS=-m pytest $(TESTS_DIR) -v
COVERAGE=coverage
PEP8=pycodestyle

DEV_CONFIG_PATH?='etc/service-dev.yaml'
TEST_CONFIG_PATH?='etc/service-dev.yaml'

all: help

.PHONY: help clean clean-pyc clean-test run test coverage check

help:
	@echo "help - show this help"
	@echo "run - start application"
	@echo "clean - remove artifacts"
	@echo "test - run tests"
	@echo "coverage - run tests with code coverage"
	@echo "check - check code style"

clean: clean-pyc clean-test

clean-pyc:
	@find . -name '*.py[cod]' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -rf {} +
	@find . -name '*$py.class' -exec rm -rf {} +

clean-test:
	@rm -rf $(COVERAGE_HTML_REPORT_DIR)

run:
	CONFIG_PATH=$(DEV_CONFIG_PATH) PYTHONPATH=$(PYTHONPATH) $(PYTHON) $(BIN_DIR)/service.py

test: clean
	CONFIG_PATH=$(TEST_CONFIG_PATH) PYTHONPATH=$(PYTHONPATH) $(PYTHON) $(TESTS_ARGS)

coverage: clean
	CONFIG_PATH=$(TEST_CONFIG_PATH) \
	PYTHONPATH=$(PYTHONPATH) $(COVERAGE) run --branch \
	                --source=$(SOURCE_DIR) \
	                $(TESTS_ARGS)
check: pep8

jupyter:
	jupyter notebook benchmark

pep8:
	$(PEP8) $(SOURCE_DIR) $(TESTS_DIR) $(BIN_DIR)
