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

RUN gh auth login --with-token < cat /run/secrets/github_token
# Clone the latest release from the private repo
# Replace 'your_username/your_private_repo' with the actual path to your GitHub repository
RUN gh release download -R KyberCritter/pygskin --pattern "*.whl"

# Install the downloaded .whl file with pip
# Note: This assumes only one .whl file is downloaded. Adjust as necessary.
COPY requirements_docker.txt /app/requirements.txt
COPY ./*.whl /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# RUN pip install -r 
RUN pip install --no-cache-dir ./*.whl

# Copy the rest of your application's code into the container
COPY . /app

RUN chmod u+x /app/docker-entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["sh","/app/docker-entrypoint.sh"]

CMD ["python", "myproject/manage.py", "runserver", "0.0.0.0:8000"]
