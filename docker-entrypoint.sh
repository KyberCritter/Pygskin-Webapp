#!/bin/sh

echo "Flushing..."
python manage.py flush --noinput
echo "Making and applying Django migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
echo "Creating superuser"
python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
echo "Loading database dump"
python manage.py loaddata /app/data_dump.json
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
# Execute the command
exec "$@"
