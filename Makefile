# Define variables
ENV_FILE=.env
ENV=local

# Default target
all: build

# Setup the application
build: install_deps set_env generate_env collect_static migrate setup_waffle_switches

# Install dependencies
install_deps:
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
generate_env:

	@echo "Setting ENV to ${ENV}"
	op inject --in-file .env.tpl --out-file ${ENV_FILE}
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

# Run the application
run:
	poetry run python manage.py runserver

# Run unit tests
test: integration unit

# Run Python unit tests
unit:
	poetry run pytest

# Run JavaScript unit tests
integration:
	npm test

# Clean up (optional)
clean:
	rm -rf staticfiles
	rm -f ${ENV_FILE}
	find . -name "*.pyc" -exec rm -f {} \;

.PHONY: all build install_deps set_env generate_env collect_static migrate setup_waffle_switches run test unit integration clean
