#!/bin/sh

if [ -n "$RDS_INSTANCE_ADDRESS" ]; then
    echo "Waiting for postgres..."

    while ! nc -z $RDS_INSTANCE_ADDRESS 5432; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate
python manage.py waffle_switch search-sort-radio-buttons off --create # create switch with default setting
python manage.py waffle_switch display-result-tags off --create # create display tags switch with default off


gunicorn --bind 0.0.0.0:8000 core.wsgi:application --workers 2 --threads 4
