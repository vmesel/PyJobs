.PHONY: help

export PYTHONPATH=pyjobs/

export DJANGO_SETTINGS_MODULE=pyjobs.settings.test

export SECRET_KEY=123321

clean: ## Clean environment
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@rm -f .coverage
	@rm -f *.log

help:  ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check:  ## Run static code checks
	@flake8 .
	@isort --check

test:  ## Run unit tests
	@py.test -x .

coverage: ## Run unit tests coverage
	@py.test -x --cov ramos/ --cov-report=xml --cov-report=term-missing tests/

check-python-import:
	@isort --check

fix-python-import:
	@git diff origin/master --name-only | grep py | xargs isort -ri

outdated: ## Show outdated dependencies
	@pip list --outdated --format=columns

install:  ## Install development dependencies
	@pip install -r requirements.txt

run:
	python pyjobs/manage.py runserver