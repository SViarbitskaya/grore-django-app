#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# Python virtual environtment
python manage.py migrate
python manage.py generate_embeddings
python manage.py runserver ${DJANGO_HOST}:${DJANGO_PORT}
