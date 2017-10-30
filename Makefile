package = oregoninvasiveshotline
distribution = psu.oit.arc.$(package)
egg_name = $(distribution)
egg_info = $(egg_name).egg-info

venv ?= .env
venv_python ?= python3
bin = $(venv)/bin
env ?= stage


venv: $(venv)
$(venv):
	$(venv_python) -m venv $(venv)

egg-info: $(egg_info)
$(egg_info):
	$(bin)/python setup.py egg_info

install: $(venv) $(egg_info)
	$(venv)/bin/pip install -r requirements.txt
reinstall: clean-install install

init: install
	@$(bin)/runcommand init
reinit: clean-egg-info clean-venv init

test: install
	@$(bin)/runcommand test
coverage: install
	$(bin)/runcommand coverage
run:
	@$(bin)/runcommand runserver

clean: clean-pyc
clean-all: clean-build clean-coverage clean-dist clean-egg-info clean-pyc clean-venv
clean-arctasks:
	$(bin)/pip uninstall --yes psu.oit.arc.tasks || echo "ARCTasks not installed"
clean-build:
	rm -rf build
clean-coverage:
	rm -f .coverage
clean-dist:
	rm -rf dist
clean-egg-info:
	rm -rf $(egg_info)
clean-install:
	$(bin)/pip uninstall $(distribution)
clean-pyc:
	find . -name __pycache__ -type d -print0 | xargs -0 rm -r
	find . -name '*.py[co]' -type f -print0 | xargs -0 rm
clean-venv:
	rm -rf $(venv)

.PHONY = \
    init \
    reinit \
    venv \
    install \
    reinstall \
    egg-info \
    install-arctasks \
    reinstall-arctasks \
    test \
    coverage \
    run-services \
    run \
    deploy \
    clean \
    clean-all \
    clean-arctasks \
    clean-build \
    clean-coverage \
    clean-dist \
    clean-egg-info \
    clean-install \
    clean-pyc \
    clean-venv
