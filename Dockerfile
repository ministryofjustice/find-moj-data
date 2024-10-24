FROM node:23-bullseye AS node_builder

WORKDIR /app
COPY . .

RUN npm install --omit=dev

# The builder image, used to build the virtual environment
FROM python:3.11-buster AS builder

WORKDIR /app
COPY --from=node_builder /app .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install poetry via pip
RUN pip install poetry==1.7.1

ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_CACHE_DIR=/tmp/poetry_cache

# Update and install dependencies for compiling .po files
RUN apt-get update && \
  apt-get install --no-install-recommends -y make gettext

COPY pyproject.toml poetry.lock Makefile ./
COPY lib ./lib
COPY locale ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR
RUN make compilemessages

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.11-slim-buster AS runtime

# Update and Install Netcat
RUN apt-get update && \
  apt-get install --no-install-recommends -y netcat

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
  PATH="/app/.venv/bin:$PATH"

# copy project and dependencies
COPY . .
COPY --from=builder /app/static ./static
COPY --from=builder /app/locale ./locale
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

RUN chmod +x ./scripts/app-entrypoint.sh

RUN python manage.py collectstatic --noinput

# Use a non-root user
RUN addgroup --gid 31337 --system appuser \
  && adduser --uid 31337 --system appuser --ingroup appuser
RUN chown --recursive appuser:appuser /app

USER 31337

EXPOSE 8000

ENTRYPOINT [ "./scripts/app-entrypoint.sh" ]
