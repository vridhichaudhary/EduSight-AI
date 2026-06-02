#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Load initial data if required (can add conditional later)
echo "Seeding demo student data if not exists..."
python manage.py seed_demo

# Start Gunicorn processes
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
