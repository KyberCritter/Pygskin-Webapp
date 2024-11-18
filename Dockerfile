# Use the official Python 3.12.3 slim image as a base
FROM python:3.12.3-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy all project files into the container
COPY . /app

# Install dependencies, including the downloaded .whl file
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy entrypoint script and make it executable
RUN chmod u+x /app/docker-entrypoint.sh

# Expose the port for the web server (Gunicorn will run on 8000)
EXPOSE 8000

# Default entrypoint script
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]

# Ensure the directory for static files exists and has correct permissions
RUN mkdir -p /app/staticfiles && chown -R www-data:www-data /app/staticfiles

# Collect static files when building the Docker image
RUN python myproject/manage.py collectstatic --noinput

# Set the working directory to the Django project directory
WORKDIR /app/myproject/

# CMD will be overwritten in docker-compose.yml based on which service is being started
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000", "--reload"]
