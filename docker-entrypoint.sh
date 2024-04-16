#!/bin/sh

echo "${RTE} runtime environment, running entrypoint"
if [ "$RTE" = "dev" ]; then
    echo "Making and applying Django migrations..."
    python myproject/manage.py flush --noinput
    python myproject/manage.py makemigrations --noinput
    python myproject/manage.py migrate --noinput
    python myproject/manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
elif [ "$RTE" = "setup" ]; then
    echo "Making and applying Django migrations..."
    python myproject/manage.py makemigrations
    python myproject/manage.py migrate --noinput
    python myproject/manage.py createsuperuser --noinput
elif [ "$RTE" = "prod" ]; then
    python manage.py check --deploy
    # python manage.py collectstatic --noinput
fi

echo "Starting server..."
# Execute the command
exec "$@"