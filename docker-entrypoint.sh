#!/bin/sh

echo "Waiting for Postgres to be ready..."
while ! ncat -z db 5432; do
  sleep 0.1
done
echo "Postgres is ready."

# Check if the database is initialized
echo "Checking if the database exists..."
RESULT=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -tc "SELECT 1 FROM pg_database WHERE datname='$POSTGRES_DB'")
if [ "$RESULT" != "1" ]; then
  echo "Database does not exist. Initializing..."
  PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -c "CREATE DATABASE $POSTGRES_DB"
else
  echo "Database already exists."
fi

echo "Making and applying Django migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Creating superuser"
python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL

# echo "Loading database dump"
# python manage.py loaddata /app/data_dump.json

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
