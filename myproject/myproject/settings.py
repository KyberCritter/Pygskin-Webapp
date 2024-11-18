from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG").upper() == "True"

# Cybercoach loading
PATH_TO_CYBERCOACHES = "/app/myproject/pygskin_webapp/cybercoaches" if os.getenv("RUNNING_ON") == "DOCKER" else "./myproject/pygskin_webapp/cybercoaches"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    ".pygskin.com",
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pygskin_webapp',
    'django_celery_beat',  # Add this for Celery Beat to manage periodic tasks
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',  # Use the service name defined in docker-compose.yml
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

STATICFILES_DIRS = [
    BASE_DIR / "static",  # Assuming you have a `static` folder in your project root
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_ROOT = "/app/staticfiles"
STATIC_URL = '/static/'


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# HTTPS
CSRF_COOKIE_DOMAIN = 'pygskin.com' if not DEBUG else "localhost"
CSRF_COOKIE_SECURE = True if not DEBUG else False
SESSION_COOKIE_SECURE = True if not DEBUG else False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_VIEW = "pygskin_webapp.views.rate_limit_error"

# Email subscription
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
TARGET_EMAIL = os.getenv("TARGET_EMAIL")    # For testing purposes

# ===========================
# Celery Configuration
# ===========================

# Broker URL for Celery (using Redis as the broker)
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')  # Ensure you're using the correct Redis service name from docker-compose

# Backend URL for Celery to store results (using Redis)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')  # Use the same Redis URL for the result backend

# Celery Task Serialization Format
CELERY_TASK_SERIALIZER = 'json'

# Celery Time Zone (make sure to align this with your Django settings)
CELERY_TIMEZONE = TIME_ZONE

# Celery Accept Content Type (tasks will be serialized as JSON)
CELERY_ACCEPT_CONTENT = ['json']

# Celery Enable UTC (set to False to use local time)
CELERY_ENABLE_UTC = True

# Celery Beat schedule (optional, but for periodic tasks)
CELERY_BEAT_SCHEDULE = {
    'my-periodic-task': {
        'task': 'pygskin_webapp.tasks.my_periodic_task',  # Full path to the task
        'schedule': 10.0,  # Every 10 seconds, adjust this as needed
    },
}

# ===========================
# Email Configuration (for sending emails)
# ===========================

# Email backend configuration for using Mailgun or any SMTP provider
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'  # Change this to your provider's SMTP server if not using Mailgun
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('MAILGUN_USERNAME')  # Mailgun username or other provider credentials
EMAIL_HOST_PASSWORD = os.getenv('MAILGUN_PASSWORD')  # Mailgun password or other provider credentials
DEFAULT_FROM_EMAIL = os.getenv('MAILGUN_EMAIL')  # From email address (e.g., your-email@mailgun.com)
