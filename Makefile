# Define variables
ENV_FILE := .env
ENV := local

# Default target
all: build

# Setup the application
build: install_deps set_env $(ENV_FILE) collect_static migrate setup_waffle_switches messages

# Install Python dependencies
install_python_deps:
	if ! command -v poetry >/dev/null 2>&1; then \
		echo "Poetry is not installed. Please install it from https://python-poetry.org/docs/#installation"; \
		exit 1; \
	fi
	poetry install

# Install Node.js dependencies
install_npm_deps:
	if ! command -v npm >/dev/null 2>&1; then \
		echo "npm is not installed. Please install it from https://nodejs.org/"; \
		exit 1; \
	fi
	npm install

# Install dependencies
install_deps:
	if ! command -v op >/dev/null 2>&1; then \
		echo "1password CLI is not installed. Please install it from https://1password.com/downloads/"; \
		exit 0; \
	fi
	if ! command -v npm >/dev/null 2>&1; then \
		echo "npm is not installed. Please install it from https://nodejs.org/"; \
		exit 1; \
	fi
	if ! command -v chromedriver >/dev/null 2>&1; then \
		echo "Chromedriver is not installed. Please install it from https://sites.google.com/a/chromium.org/chromedriver/downloads"; \
		exit 1; \
	fi
	if ! command -v poetry >/dev/null 2>&1; then \
		echo "Poetry is not installed. Please install it from https://python-poetry.org/docs/#installation"; \
		exit 1; \
	fi
	@make install_python_deps
	@make install_npm_deps

# Generate .env file
$(ENV_FILE): .env.tpl
	@echo "Setting ENV to ${ENV}"
	op inject --in-file .env.tpl --out-file $(ENV_FILE)
	@echo "Optionally, set CATALOGUE_TOKEN in ${ENV_FILE}"

# Collect static files
collect_static:
	poetry run python manage.py collectstatic --noinput

# Run migrations
migrate:
	poetry run python manage.py migrate

# Setup waffle switches
setup_waffle_switches:
	poetry run python manage.py waffle_switch search-sort-radio-buttons off --create
	poetry run python manage.py waffle_switch display-result-tags off --create

# Run makemessages
messages:
	poetry run python manage.py makemessages --locale=en --ignore venv
	poetry run python manage.py compilemessages --ignore venv

compilemessages:
	poetry run python manage.py compilemessages --ignore venv

# Run the application
run:
	poetry run python manage.py runserver

# Run unit tests
test: unit integration lint

# Run Python unit tests
unit:
	poetry run pytest --cov -m 'not slow'
	npm test

# Run integration tests. Requires chromedriver - version works with chromedriver 127.0.1 use - `npm install -g chromedriver@127.0.1`
integration:
	poetry run pytest tests/integration --axe-version 4.9.1 --chromedriver-path $$(which chromedriver)


# Install project dependencies for GitHub Actions
gha_install_project: install_python_deps install_npm_deps
	poetry install --no-interaction --no-root
	sudo apt-get install gettext

gha_fast_tests:
	poetry run pytest --cov -m 'not slow and not datahub' --doctest-modules

gha_slow_tests:
	poetry run pytest tests/integration --axe-version 4.9.1 --chromedriver-path /usr/local/bin/chromedriver

# Setup and cache Node.js dependencies in GitHub Actions
gha_setup_node:
	@make install_npm_deps

# Clean up (optional)
clean:
	rm -rf staticfiles
	rm -f $(ENV_FILE)
	find . -name "*.pyc" -exec rm -f {} \;

lint:
	pre-commit run --all-files

.PHONY: all build install_deps set_env collect_static migrate setup_waffle_switches messages compilemessages run test unit integration clean lint
