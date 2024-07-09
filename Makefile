.PHONY: clean ## Remove build and cache files
clean:
	rm -rf */*.egg-info
	rm -rf build
	rm -rf dist
	rm -rf .pytest_cache
	# Remove all pycache
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf

# define the name of the virtual environment directory
VENV := .venv

$(VENV)/bin/activate:
	pip install virtualenv
	virtualenv -p `which python3` .venv

# default target, when make executed without arguments
all: venv

# venv is a shortcut target
venv: $(VENV)/bin/activate

.PHONY: install ## sets up environment and installs requirements
install: venv
	$(VENV)/bin/pip install -U pip setuptools wheel
	$(VENV)/bin/pip install -e .[dev]

.PHONY: lint ## Runs flake8 on src, exit if critical rules are broken
lint: venv
	# stop the build if there are Python syntax errors or undefined names
	$(VENV)/bin/flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	$(VENV)/bin/flake8 src --count --exit-zero --statistics

.PHONY: format ## Runs black on src
format: venv
	$(VENV)/bin/black src

.PHONY: test ## Run pytest
test: venv
	$(VENV)/bin/python3 -m unittest discover -s src
