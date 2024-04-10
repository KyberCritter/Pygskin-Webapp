# Use the official Python 3.12 slim image as a base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies for GitHub CLI and wget
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        gnupg \
        software-properties-common \
        lsb-release \
        curl \
    && echo "deb [signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && apt-get update \
    && apt-get install -y gh \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up environment variable for GitHub access token
ARG GITHUB_TOKEN

# Use curl to fetch the latest release data from GitHub API and parse the .whl asset download URL
# Then, use curl again to download the .whl file using the GITHUB_TOKEN for authorization
RUN curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/KyberCritter/pygskin/releases/latest" | \
    grep -Eo '"browser_download_url": "[^"]+\.whl"' | \
    grep -Eo 'https:[^"]+' | \
    xargs curl -s -L -o app_package.whl -H "Authorization: token $GITHUB_TOKEN"

# Install the downloaded .whl file with pip
COPY requirements_docker.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install --no-cache-dir app_package.whl

RUN pip install -r requirements.txt

# Copy the rest of your application's code into the container
COPY . /app

RUN chmod u+x /app/docker-entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["sh","/app/docker-entrypoint.sh"]

CMD ["python", "myproject/manage.py", "runserver", "0.0.0.0:8000"]