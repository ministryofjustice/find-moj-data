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
python manage.py waffle_switch show_is_nullable_in_table_details_column off --create # create isnullable column switch with default off
python manage.py waffle_switch new_subject_areas on --create # remove this once deployed
python manage.py waffle_flag home_variant_a --testing --create
python manage.py waffle_flag home_variant_b --testing --create

gunicorn --bind 0.0.0.0:8000 core.wsgi:application --workers 2 --threads 4
