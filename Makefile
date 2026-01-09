# Define variables
ENV_FILE := .env
ENV := local
BUILD_COMMAND := uv run
LOCAL_IMAGE_TAG := find-moj-data:local

# Default target
all: build

# Setup the application
build: install_deps set_env $(ENV_FILE) assets migrate setup_waffle_switches install-hooks update-hooks

# Install Python dependencies
install_python_deps:
	if ! command -v uv >/dev/null 2>&1; then \
		echo "Uv is not installed. Please install it from https://docs.astral.sh/uv/getting-started/installation/"; \
		exit 1; \
	fi
	uv sync

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

# Install trivy for scanning docker images
install_trivy:
	if ! command -v trivy >/dev/null 2>&1; then \
		echo "Trivy is not installed. Please install it from https://trivy.dev/latest/getting-started/installation/"; \
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
	$(BUILD_COMMAND) python manage.py collectstatic --noinput

# Run migrations
migrate:
	$(BUILD_COMMAND) python manage.py migrate

# Setup waffle switches
setup_waffle_switches:
	$(BUILD_COMMAND) python manage.py waffle_switch search-sort-radio-buttons off --create # create switch with default setting
	$(BUILD_COMMAND) python manage.py waffle_switch display-result-tags on --create # create display tags switch with default off
	$(BUILD_COMMAND) python manage.py waffle_switch show_is_nullable_in_table_details_column off --create # create isnullable column switch with default off

# Run the application
run:
	$(BUILD_COMMAND) python manage.py runserver

# Run unit tests
test: unit integration lint

# Run Python and Javascript unit tests
unit:
	$(BUILD_COMMAND) pytest --cov -m 'not slow and not datahub' --doctest-modules
	npm test

# Run integration tests. Requires chromedriver - version works with chromedriver 127.0.1 use - `npm install -g chromedriver@127.0.1`
integration:
	TESTING=true $(BUILD_COMMAND)  pytest tests/integration --axe-version 4.9.1 --chromedriver-path $$(which chromedriver)

end_to_end:
	TESTING=true $(BUILD_COMMAND)  pytest tests/end_to_end --chromedriver-path $$(which chromedriver)

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

# Run all linting (pre-commit hooks)
lint:
	$(BUILD_COMMAND) pre-commit run --all-files

# Run ruff format check
format-check:
	$(BUILD_COMMAND) ruff format --check .

# Run ruff format (fix)
format:
	$(BUILD_COMMAND) ruff format .

# Run ruff lint check
lint-check:
	$(BUILD_COMMAND) ruff check .

# Run ruff lint with autofix
lint-fix:
	$(BUILD_COMMAND) ruff check --fix .

# Install pre-commit hooks (run once after cloning)
install-hooks:
	$(BUILD_COMMAND) pre-commit install

# Update pre-commit hooks to latest versions
update-hooks:
	$(BUILD_COMMAND) pre-commit autoupdate

build-image:
	docker build  -t $(LOCAL_IMAGE_TAG) .

scan: install_trivy build-image
	trivy image --scanners vuln $(LOCAL_IMAGE_TAG)


.PHONY: all build install_deps set_env assets migrate setup_waffle_switches run test unit integration clean lint format format-check lint-check lint-fix install-hooks update-hooks build-image scan install_trivy
