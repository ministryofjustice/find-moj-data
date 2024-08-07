# Define variables
ENV_FILE := .env
ENV := local

# Default target
all: build

# Setup the application
build: install_deps set_env $(ENV_FILE) collect_static migrate setup_waffle_switches compile_messages

# Install dependencies
install_deps:
	if ! command -v op >/dev/null 2>&1; then \
		echo "1password CLI is not installed. Please install it from https://1password.com/downloads/"; \
		exit 1; \
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
	poetry install
	npm install

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
	poetry run python manage.py makemessages --locale=en

# Compile messages
compile_messages:
	poetry run python manage.py compilemessages

# Run the application
run:
	poetry run python manage.py runserver

# Run unit tests
test: unit integration

# Run Python unit tests
unit:
	poetry run pytest --cov -m 'not slow'
	npm test

# Run integration tests. Requires chromedriver - version works with chromedriver 127.0.1 use - `npm install -g chromedriver@127.0.1`
integration:
	export CHROMEDRIVER_PATH=$(which chromedriver)
	poetry run pytest tests/integration --axe-version 4.9.1 --chromedriver-path ${CHROMEDRIVER_PATH}


# Clean up (optional)
clean:
	rm -rf staticfiles
	rm -f $(ENV_FILE)
	find . -name "*.pyc" -exec rm -f {} \;

.PHONY: all build install_deps set_env collect_static migrate setup_waffle_switches messages compile_messages run test unit integration clean
