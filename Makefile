package = oregoninvasiveshotline
distribution = psu.oit.arc.$(package)
egg_name = $(distribution)
egg_info = $(egg_name).egg-info
venv ?= .env
venv_python ?= python3.3
bin = $(venv)/bin

init: $(venv)
	@$(bin)/pip install git+https://github.com/PSU-OIT-ARC/arctasks#egg=psu.oit.arc.tasks
	@$(bin)/inv init
	@$(bin)/inv coverage
reinit: clean-venv clean-install init

venv: $(venv)
$(venv):
	virtualenv -p $(venv_python) $(venv)
clean-venv:
	rm -rf $(venv)

install: venv $(egg_info)
reinstall: clean-install install
$(egg_info):
	$(venv)/bin/pip install -r requirements.txt
clean-install:
	rm -rf $(egg_info)

clean:
	@$(bin)/inv clean
clean-all: clean-coverage clean-install clean-pyc clean-venv
	rm -rf build dist
clean-pyc:
	find . -name __pycache__ -type d -print0 | xargs -0 rm -r

test: install
	@$(bin)/inv test
coverage: install
	$(bin)/inv coverage
clean-coverage:
	rm -f .coverage

run:
	@$(bin)/inv runserver

to ?= stage
deploy:
	$(bin)/inv configure --env $(to) deploy

.DEFAUL_GOAL = run
.PHONY = \
    init reinit venv install reinstall test coverage \
    clean-venv clean-install clean-coverage \
    clean clean-all clean-pyc
