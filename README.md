## Quick start

You will need npm (for javascript dependencies) and poetry (for python dependencies).

1. Run `poetry install` to install python dependencies
2. Copy `.env.example` to `.env`.
3. You wil need to obtain an access token from Datahub catalogue and populate the `CATALOGUE_TOKEN` var in .env to be able to retrieve search data.
   https://datahub.apps-tools.development.data-platform.service.justice.gov.uk/settings/tokens
4. Run `poetry run python manage.py runserver`

Run `npm install` and then `npm run sass` to compile the stylesheets.

## Current Endpoints

/search

![Screenshot of the service showing the search page](image.png)

## Testing

- Python unit tests: `pytest -m 'not slow'`
- Javascript unit tests: `npm test`
- Selenium tests: `pytest -m 'slow'`
