# Define variables
ENV_FILE := .env
ENV := local

# Default target
all: build

# Setup the application
build: install_deps set_env $(ENV_FILE) assets migrate setup_waffle_switches

# Install Python dependencies
install_python_deps:
	if ! command -v poetry >/dev/null 2>&1; then \
		echo "Poetry is not installed. Please install it from https://python-poetry.org/docs/#installation"; \
		exit 1; \
	fi
	poetry install --no-root

# Install Node.js dependencies
install_npm_deps:
	if ! command -v npm >/dev/null 2>&1; then \
		echo "npm is not installed. Please install it from https://nodejs.org/"; \
		exit 1; \
	fi
	npm install

# Install dependencies
install_deps: install_npm_deps install_python_deps
	if ! command -v op >/dev/null 2>&1; then \
		echo "1password CLI is not installed. Please install it from https://1password.com/downloads/"; \
		exit 1; \
	fi
	if ! command -v chromedriver >/dev/null 2>&1; then \
		echo "Chromedriver is not installed. Please install it from https://sites.google.com/a/chromium.org/chromedriver/downloads"; \
		exit 1; \
	fi

# Generate .env file
$(ENV_FILE): .env.tpl
	@echo "Setting ENV to ${ENV}"
	op inject --in-file .env.tpl --out-file $(ENV_FILE)
	@echo "Optionally, set CATALOGUE_TOKEN in ${ENV_FILE}"

# Collect static files
assets:
	npm run dependencies
	poetry run python manage.py collectstatic --noinput

# Run migrations
migrate:
	poetry run python manage.py migrate

# Setup waffle switches
setup_waffle_switches:
	python manage.py waffle_switch search-sort-radio-buttons off --create # create switch with default setting
	python manage.py waffle_switch display-result-tags on --create # create display tags switch with default off
	python manage.py waffle_switch show_is_nullable_in_table_details_column off --create # create isnullable column switch with default off
	python manage.py waffle_switch new_subject_areas on --create # remove this once deployed

# Run the application
run:
	poetry run python manage.py runserver

# Run unit tests
test: unit integration lint

# Run Python and Javascript unit tests
unit:
	poetry run pytest --cov -m 'not slow and not datahub' --doctest-modules
	npm test

# Run integration tests. Requires chromedriver - version works with chromedriver 127.0.1 use - `npm install -g chromedriver@127.0.1`
integration:
	TESTING=true poetry run pytest tests/integration --axe-version 4.9.1 --chromedriver-path $$(which chromedriver)

end_to_end:
	TESTING=true poetry run pytest tests/end_to_end --chromedriver-path $$(which chromedriver)

# Get npm cache directory and store it in a file
export_npm_cache_dir:
	@echo "Fetching npm cache directory..."
	@npm config get cache > .npm_cache_dir
	@echo "NPM cache directory stored in .npm_cache_dir"

# Clean up (optional)
clean:
	rm -rf staticfiles
	rm -f $(ENV_FILE)
	find . -name "*.pyc" -exec rm -f {} \;

lint:
	pre-commit run --all-files

.PHONY: all build install_deps set_env assets migrate setup_waffle_switches run test unit integration clean lint
