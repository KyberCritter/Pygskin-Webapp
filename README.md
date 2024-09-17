# Setup

1. Clone the pygskin-webapp repo's cs-project branch.
2. Create `.env` file at the root with the dummy contents from the **.env** section of `README.md`.
3. Replace the empty usernames, email addresses, and passwords with your desired values.
4. Download `pygskin-0.1.1-py3-none-any.whl` from Pygskin releases page and copy to root of repo.
5. Create an empty directory called `certs` in the root of the repo.
6. Run `docker compose build` from root.
7. Run `docker compose up` from root.
8. In your browser, visit `localhost`, which should show the Pygskin homepage.

## .env

SECRET_KEY=""
DEBUG="True"
RUNNING_ON="DOCKER"

DJANGO_SUPERUSER_USERNAME=""
DJANGO_SUPERUSER_EMAIL=""
DJANGO_SUPERUSER_PASSWORD=""

POSTGRES_DB="mydatabase"
POSTGRES_USER=""
POSTGRES_PASSWORD=""

UMAMI_DB="umami"
UMAMI_USER=""
UMAMI_PASSWORD=""

MAILGUN_API_KEY=""
MAILGUN_DOMAIN=""

RTE="DEV"
GITHUB_TOKEN=""
DIGITALOCEAN_TOKEN=""
FULL_ACCESS=""
