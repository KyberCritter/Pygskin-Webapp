@echo off
setlocal

:: Load GITHUB_TOKEN from .env file
for /F "tokens=2 delims==" %%i in ('findstr GITHUB_TOKEN .env') do set GITHUB_TOKEN=%%i

:: Build the Docker image
docker build --build-arg GITHUB_TOKEN=%GITHUB_TOKEN% -t pygskin-webapp .

endlocal
