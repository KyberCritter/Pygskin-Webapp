# Setup

1. Clone the pygskin-webapp repo's cs-project branch.
2. Create `.env` file at the root with the dummy contents from the # .env section of `README.md`.
3. Download ` pygskin-0.1.1-py3-none-any.whl` from Pygskin releases page and copy to root of repo.
4. Run `docker compose build` from root.
5. Run `docker compose run` from root.
6. In your browser, visit `localhost`, which should show the Pygskin homepage.

## .env

SECRET_KEY=""
DEBUG="True"
RUNNING_ON="DOCKER"

DJANGO_SUPERUSER_USERNAME="username"
DJANGO_SUPERUSER_EMAIL="test@website.com"
DJANGO_SUPERUSER_PASSWORD="password"

POSTGRES_DB="mydatabase"
POSTGRES_USER="username"
POSTGRES_PASSWORD="password"

UMAMI_DB="umami"
UMAMI_USER="username"
UMAMI_PASSWORD="password"

MAILGUN_API_KEY=""
MAILGUN_DOMAIN=""

RTE="DEV"
GITHUB_TOKEN=""
DIGITALOCEAN_TOKEN=""
FULL_ACCESS=""
