#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# Python virtual environtment
python -m venv $APP_CACHE_ROOT/.venv
$APP_CACHE_ROOT/.venv/bin/pip install --upgrade pip
$APP_CACHE_ROOT/.venv/bin/pip install -r $APP_DJANGO_ROOT/requirements.txt
$APP_CACHE_ROOT/.venv/bin/python manage.py migrate
$APP_CACHE_ROOT/.venv/bin/python manage.py collectstatic --noinput
$APP_CACHE_ROOT/.venv/bin/python manage.py runserver ${DJANGO_HOST}:${DJANGO_PORT}

