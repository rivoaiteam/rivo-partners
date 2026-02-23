#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Seeding config..."
python manage.py seed_config

echo "Starting server..."
exec gunicorn rivo_partner.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120
