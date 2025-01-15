# Setup

1. Clone the pygskin-webapp repo's cs-project branch.
2. Create `.env` file at the root with the dummy contents from the `.env` section of `README.md`.
3. Create an empty directory called `certs` in the root of the repo.
4. Run `openssl req -x509 -newkey rsa:4096 -keyout privkey.pem -out fullchain.pem -sha256 -days 3650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=CommonNameOrHostname"` to create a "dummy" SSL certificate and private key. Move these files into the newly created `certs` directory.
5. Open a Python REPL with Django installed (probably using `python3`). Run `from django.core.management.utils import get_random_secret_key` and `get_random_secret_key()` to generate a new secret key. Paste this value (without the single quotes) between the doubles quotes of the SECRET_KEY line of `.env`.
6. Replace the empty usernames, email addresses, and passwords with your desired values.
7. Download `pygskin-0.1.2-py3-none-any.whl` from Pygskin releases page and copy to root of repo.
8. If this is your first time building the Docker containers on this machine, uncomment the portions of `docker-entrypoint.sh` that load the data dump.
9. Run `docker compose build` from root.
10. Run `docker compose up` from root.
11. In your browser, visit `localhost`, which should show a warning in your browser about an insecure connection. Ignore the warnings to procede to the Pygskin homepage.
12. Ensure that the data dump portions of `docker-entrypoint.sh` are commented out again before starting the containers again.

## .env

```shell
SECRET_KEY=""
DEBUG="False"
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

```
