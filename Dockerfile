# Use the official Python 3.12 slim image as a base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app

# Copy requirements file to the container
COPY requirements_docker.txt /app/requirements.txt

# Install dependencies including the downloaded .whl file
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --force-reinstall

RUN chmod u+x /app/docker-entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]

CMD ["python", "myproject/manage.py", "runserver", "0.0.0.0:8000"]
