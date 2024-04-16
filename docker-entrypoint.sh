#!/bin/sh

echo "${RTE} runtime environment, running entrypoint"
if [ "$RTE" = "dev" ]; then
    echo "Flushing..."
    python myproject/manage.py flush --noinput
    echo "Making and applying Django migrations..."
    python myproject/manage.py makemigrations --noinput
    python myproject/manage.py migrate --noinput
    echo "Creating superuser"
    python myproject/manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
    echo "Loading database dump"
    python myproject/manage.py loaddata data_dump.json
elif [ "$RTE" = "setup" ]; then
    echo "Making and applying Django migrations..."
    python myproject/manage.py makemigrations
    python myproject/manage.py migrate --noinput
    echo "Creating superuser"
    python myproject/manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
    echo "Loading database dump"
    python myproject/manage.py loaddata data_dump.json
elif [ "$RTE" = "prod" ]; then
    echo "Making and applying Django migrations..."
    python myproject/manage.py makemigrations
    python myproject/manage.py migrate --noinput
    echo "Creating superuser"
    python myproject/manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
    echo "Loading database dump"
    python myproject/manage.py loaddata data_dump.json
    # python myproject/manage.py collectstatic --noinput
fi

echo "Starting server..."
# Execute the command
exec "$@"