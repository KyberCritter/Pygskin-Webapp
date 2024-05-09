# Use the official Python 3.12.3 slim image as a base
FROM python:3.13.0a6-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app

ADD . /code/

# Install dependencies, including the downloaded .whl file
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod u+x /app/docker-entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]

RUN python myproject/manage.py collectstatic --noinput
WORKDIR /app/myproject/
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000", "--reload"]
