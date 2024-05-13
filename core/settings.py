import os
import sys
from pathlib import Path

import sentry_sdk
import yaml
from dotenv import load_dotenv

TRUTHY_VALUES = ["True", "true", "T", "1"]

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# loads the configs from .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = str(os.environ.get("SECRET_KEY"))

# SECURITY WARNING: don't run with debug turned on in production!
# os.environ returns string values for env vars
DEBUG_STR: str = os.environ.get("DEBUG", default="0")
DEBUG: bool = DEBUG_STR in TRUTHY_VALUES

ALLOWED_HOSTS = str(os.environ.get("DJANGO_ALLOWED_HOSTS")).split(" ")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "home.apps.HomeConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.env",
                "core.context_processors.analytics",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "Europe/London"
USE_I18N = False
USE_TZ = True

# https://whitenoise.readthedocs.io/en/latest/django.html#WHITENOISE_STATIC_PREFIX
STATIC_URL = "/static/"
FRONTEND_STATIC_BASE_URL = STATIC_URL
# https://whitenoise.readthedocs.io/en/latest/django.html#make-sure-staticfiles-is-configured-correctly
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'home.utils.storage.NonstrictManifestStaticFilesStorage'

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_DIRS = [BASE_DIR / "static"]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

SAMPLE_SEARCH_RESULTS_FILENAME = BASE_DIR / "sample_data/sample_search_page.yaml"

with open(SAMPLE_SEARCH_RESULTS_FILENAME) as f:
    SAMPLE_SEARCH_RESULTS = yaml.safe_load(f)

# Catalog settings
CATALOGUE_URL = os.environ.get("CATALOGUE_URL")
CATALOGUE_TOKEN = os.environ.get("CATALOGUE_TOKEN")
ENV = os.environ.get("ENV")

# session
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# Not actually used - Just required for LiveServerTestCase
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
# Define a service name setting for page titles
SERVICE_NAME = "Find MOJ Data"
GOV_UK_SUFFIX = "GOV.UK"

MAX_RESULTS = 10_000

LOGGING = {
    "version": 1,  # the dictConfig format version
    "disable_existing_loggers": False,  # retain the default loggers
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "DEBUG"),
    },
    "loggers": {
        "django": {
            "level": os.environ.get("DJANGO_LOG_LEVEL", "DEBUG"),
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

ANALYTICS_ID: str = os.environ.get("ANALYTICS_ID", "")
ENABLE_ANALYTICS: bool = (
    os.environ.get("ENABLE_ANALYTICS") in TRUTHY_VALUES
) and ANALYTICS_ID != ""

# Sentry Configuration
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    enable_tracing=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    environment=ENV or "local",
)
