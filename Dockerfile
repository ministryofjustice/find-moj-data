# The builder image, used to build the virtual environment
FROM python:3.11-buster as builder

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install poetry via pip
RUN pip install poetry==1.5.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# set work directory
WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.11-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# copy project
COPY . .

RUN python3 manage.py migrate --no-input \
    && python3 manage.py collectstatic --no-input

# Use a non-root user
RUN addgroup --gid 31337 --system appuser \
  && adduser --uid 31337 --system appuser --ingroup appuser
RUN chown --recursive appuser:appuser /app
USER 31337


EXPOSE 8000

# ENTRYPOINT [ "python", "manage.py", "runserver"]
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
# 
