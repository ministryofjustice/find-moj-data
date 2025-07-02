ARG ecr_path=public.ecr.aws/docker/library/
ARG alpine_version=alpine3.21
ARG python_version=python:3.13.5
ARG node_version=node:24.3

#### NODE.JS BUILD
FROM ${ecr_path}${node_version}-${alpine_version} AS node_builder
WORKDIR /app

# Install dependencies for npm install command
RUN apk add --no-cache bash

# Compile static assets
COPY package.json package-lock.json ./
COPY scripts/import-static.sh ./scripts/import-static.sh
COPY static/assets/images/guide ./static/assets/images/guide
COPY static/assets/js ./static/assets/js
COPY scss ./scss
RUN npm install --omit=dev

#### PYTHON BUILD
FROM ${ecr_path}${python_version}-${alpine_version} AS python_builder
WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# UV Environment variables
ENV UV_CACHE_DIR="/tmp/uv_cache"

# Install UV and Python dependencies to a virtualenv
COPY pyproject.toml uv.lock ./
RUN pip install uv==0.7.17
RUN uv sync --no-dev --locked && rm -rf $UV_CACHE_DIR

#### FINAL RUNTIME IMAGE
FROM ${ecr_path}${python_version}-${alpine_version} AS runtime

# Workaround for CVE-2024-6345 upgrade the installed version of setuptools to the latest version
RUN pip install -U setuptools

# Install dependencies for the runtime image
RUN apk add --no-cache bash make netcat-openbsd gettext

# Use a non-root user
ENV CONTAINER_USER=appuser \
  CONTAINER_GROUP=appuser \
  CONTAINER_UID=31337 \
  CONTAINER_GID=31337

RUN addgroup --gid ${CONTAINER_GID} --system ${CONTAINER_GROUP} \
  && adduser --uid ${CONTAINER_UID} --system ${CONTAINER_USER} --ingroup ${CONTAINER_GROUP}

USER ${CONTAINER_UID}
WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
  PATH="/app/.venv/bin:$PATH"

# Copy entrypoints
COPY --chown=${CONTAINER_USER}:${CONTAINER_GROUP} scripts/app-entrypoint.sh ./scripts/app-entrypoint.sh
COPY --chown=${CONTAINER_USER}:${CONTAINER_GROUP} manage.py ./
RUN chmod +x ./scripts/app-entrypoint.sh

# Copy compiled assets
COPY --from=node_builder --chown=${CONTAINER_USER}:${CONTAINER_GROUP} /app/static ./static
COPY --from=python_builder --chown=${CONTAINER_USER}:${CONTAINER_GROUP} ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --chown=${CONTAINER_USER}:${CONTAINER_GROUP} manage.py ./

# Copy application code
COPY --chown=${CONTAINER_USER}:${CONTAINER_GROUP} core ./core
COPY --chown=${CONTAINER_USER}:${CONTAINER_GROUP} users ./users
COPY --chown=${CONTAINER_USER}:${CONTAINER_GROUP} feedback ./feedback
COPY --chown=${CONTAINER_USER}:${CONTAINER_GROUP} datahub_client ./datahub_client
COPY --chown=${CONTAINER_USER}:${CONTAINER_GROUP} home ./home
COPY --chown=${CONTAINER_USER}:${CONTAINER_GROUP} templates ./templates
COPY --chown=${CONTAINER_USER}:${CONTAINER_GROUP} dashboard ./dashboard
COPY --chown=${CONTAINER_USER}:${CONTAINER_GROUP} userguide ./userguide


# Run django commands
RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT [ "./scripts/app-entrypoint.sh" ]
