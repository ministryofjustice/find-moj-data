#!/bin/sh

if [ -n "$RDS_INSTANCE_ADDRESS" ]; then
    echo "Waiting for postgres..."

    while ! nc -z $RDS_INSTANCE_ADDRESS 5432; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 core.wsgi:application --workers 2 --threads 4
