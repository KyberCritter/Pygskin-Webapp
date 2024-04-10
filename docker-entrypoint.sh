#!/bin/bash

echo "Applying Django migrations..."
python myproject/manage.py migrate

echo "Starting server..."
# Execute the command
exec "$@"