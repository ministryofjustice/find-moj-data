ARG ecr_path=public.ecr.aws/docker/library/
ARG alpine_version=alpine3.20
ARG python_version=python:3.11
ARG node_version=node:23

# The node builder image, used to build the virtual environment
FROM ${ecr_path}${node_version}-${alpine_version} AS node_builder

# Install dependencies for npm install command
RUN apk add --no-cache bash

WORKDIR /app
COPY . .

RUN npm install --omit=dev

# The builder image, used to build the virtual environment
FROM ${ecr_path}${python_version}-${alpine_version} AS python_builder

# Install dependencies for compiling .po files
RUN apk add --no-cache bash make gettext gcc musl-dev libffi-dev

WORKDIR /app
COPY --from=node_builder /app .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install poetry via pip
RUN pip install poetry==1.8.4

ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_CACHE_DIR=/tmp/poetry_cache

COPY pyproject.toml poetry.lock Makefile ./
COPY lib ./lib
COPY locale ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR
RUN make compilemessages

# The runtime image, used to just run the code provided its virtual environment
FROM ${ecr_path}${python_version}-${alpine_version} AS runtime

# Install dependencies for the runtime image
RUN apk add --no-cache bash make netcat-openbsd

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
  PATH="/app/.venv/bin:$PATH"

# copy project and dependencies
COPY . .
COPY --from=python_builder /app/static ./static
COPY --from=python_builder /app/locale ./locale
COPY --from=python_builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

RUN chmod +x ./scripts/app-entrypoint.sh

RUN python manage.py collectstatic --noinput

# Use a non-root user
RUN addgroup --gid 31337 --system appuser \
  && adduser --uid 31337 --system appuser --ingroup appuser
RUN chown --recursive appuser:appuser /app

USER 31337

EXPOSE 8000

ENTRYPOINT [ "./scripts/app-entrypoint.sh" ]
