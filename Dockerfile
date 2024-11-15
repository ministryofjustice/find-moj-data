ARG ecr_path=public.ecr.aws/docker/library/
ARG alpine_version=alpine3.20
ARG python_version=python:3.11
ARG node_version=node:23

#### NODE.JS BUILD

FROM ${ecr_path}${node_version}-${alpine_version} AS node_builder
WORKDIR /app

# Install dependencies for npm install command
RUN apk add --no-cache bash

# Compile static assets
COPY package.json package-lock.json ./
COPY scripts/import-static.sh ./scripts/import-static.sh
COPY static/assets/js ./static/assets/js
COPY scss ./scss
RUN npm install --omit=dev

#### PYTHON BUILD

FROM ${ecr_path}${python_version}-${alpine_version} AS python_builder
WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_CACHE_DIR=/tmp/poetry_cache

# Install python dependencies to a virtualenv
COPY pyproject.toml poetry.lock ./
COPY lib ./lib
RUN pip install poetry==1.8.4
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

#### FINAL RUNTIME IMAGE

FROM ${ecr_path}${python_version}-${alpine_version} AS runtime

# Workaround for CVE-2024-6345 upgrade the installed version of setuptools to the latest version
RUN pip install -U setuptools

# Install dependencies for the runtime image
RUN apk add --no-cache bash make netcat-openbsd gettext

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
  PATH="/app/.venv/bin:$PATH"

# copy project and dependencies
COPY . .
COPY --from=node_builder /app/static ./static
COPY --from=python_builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
RUN chmod +x ./scripts/app-entrypoint.sh

RUN python manage.py collectstatic --noinput
RUN python manage.py compilemessages

# Use a non-root user
RUN addgroup --gid 31337 --system appuser \
  && adduser --uid 31337 --system appuser --ingroup appuser
RUN chown --recursive appuser:appuser /app

USER 31337

EXPOSE 8000

ENTRYPOINT [ "./scripts/app-entrypoint.sh" ]
