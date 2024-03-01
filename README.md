# Data catalogue

This repository deploys a data catalogue built on [Datahub](https://datahubproject.io), with a GOV.UK styled Frontend (Find MOJ Data.)

## Environments
- [Datahub (dev)](https://datahub-catalogue-dev.apps.live.cloud-platform.service.justice.gov.uk/)
- [Find MOJ data (dev)](https://data-platform-find-moj-data-dev.apps.live.cloud-platform.service.justice.gov.uk/)

## Related repositories
- [data-catalogue-metadata](https://github.com/ministryofjustice/data-catalogue-metadata) (internal) contains JSON files used to populate the catalogue in development

## Datahub (Backend)

### Administration via command line

#### First time setup

Run `datahub init` and provide the following credentials

- server: https://data-platform-datahub-catalogue-dev.apps.live.cloud-platform.service.justice.gov.uk
- token: `<generate PAT via the UI>`

You may also need to set the environment variable `export DATAHUB_GMS_URL="https://data-platform-datahub-catalogue-dev.apps.live.cloud-platform.service.justice.gov.uk/api/gms"`

#### Import metadata into a Datahub lite

[Datahub lite](https://datahubproject.io/docs/datahub_lite/) is a developer interface for local debugging.

lite_sink.yaml:

```yaml
pipeline_name: datahub_source_1
datahub_api:
  server: "https://data-platform-datahub-catalogue-dev.apps.live.cloud-platform.service.justice.gov.uk/api/gms" 
  token: "xxxxx"
source:
  type: datahub
  config:
    include_all_versions: false
    pull_from_datahub_api: true
sink:
  type: datahub-lite
```

```
datahub ingest -c lite_sink.yaml

datahub lite ls
```

## Find MOJ Data (Frontend)

### Quick start

You will need npm (for javascript dependencies) and poetry (for python dependencies).

1. Run `poetry install` to install python dependencies
2. Copy `.env.example` to `.env`.
3. You wil need to obtain an access token from Datahub catalogue and populate the
`CATALOGUE_TOKEN` var in .env to be able to retrieve search data.
4. Run `poetry run python manage.py runserver`

Run `npm install` and then `npm run sass` to compile the stylesheets.

### Current Endpoints

/search

![Screenshot of the service showing the search page](image.png)

### Contributing

Run `pre-commit install` from inside the poetry environment to set up pre commit hooks.

- Linting and formatting handled by `black`, `flake8`, `pre-commit`, and `isort`
  - `isort` is configured in `pyproject.toml`
- `detect-secrets` is used to prevent leakage of secrets
- `sync_with_poetry` ensures the versions of the modules in the pre-commit specification
  are kept in line with those in the `pyproject.toml` config.

### Testing

- Python unit tests: `pytest -m 'not slow'`
- Javascript unit tests: `npm test`
- Selenium tests: `pytest -m 'slow'`
