ARG ecr_path=public.ecr.aws/docker/library/
ARG alpine_version=alpine3.23
ARG python_version=python:3.13.5
ARG node_version=node:24.3

#### NODE.JS BUILD
FROM ${ecr_path}${node_version}-${alpine_version} AS node_builder
WORKDIR /app

# Install dependencies for npm install command
RUN apk update && apk upgrade --no-cache && apk add --no-cache bash

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

RUN apk update && apk upgrade --no-cache && apk add --no-cache gcc musl-dev libffi-dev

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# UV Environment variables
ENV UV_CACHE_DIR="/tmp/uv_cache"

# Install UV and Python dependencies to a virtualenv
COPY pyproject.toml uv.lock ./
RUN pip install --upgrade pip setuptools wheel
RUN pip install uv==0.7.17
RUN uv sync --no-dev --locked && rm -rf $UV_CACHE_DIR
RUN uv pip install 'aiohttp>=3.12.15' 'urllib3>=2.5.0' 'pip>=25.3'

#### FINAL RUNTIME IMAGE
FROM ${ecr_path}${python_version}-${alpine_version} AS runtime

# Upgrade Python packaging tooling to mitigate known pip/setuptools vulnerabilities
RUN pip install --upgrade pip setuptools wheel

# Install dependencies for the runtime image
RUN apk update \
  && apk upgrade --no-cache \
  && apk add --no-cache bash make netcat-openbsd gettext
