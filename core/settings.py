import os
import sys
from pathlib import Path
from socket import gaierror, gethostbyname, gethostname

import sentry_sdk
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

try:
    ALLOWED_HOSTS.append(gethostbyname(gethostname()))
except gaierror:
    pass

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
    "django_prometheus",
    "users",
    "waffle",
]

if os.environ.get("AZURE_AUTH_ENABLED", "true") != "false":
    INSTALLED_APPS.append("azure_auth")

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.CustomErrorMiddleware",
    "waffle.middleware.WaffleMiddleware",
    # Prometheus needs to be the last middleware in the list.
    # Avoid appending to this list and rather insert into -1.
    "django_prometheus.middleware.PrometheusAfterMiddleware",
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

AUTH_USER_MODEL = "users.CustomUser"


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "Europe/London"
USE_I18N = False
USE_TZ = True

# https://whitenoise.readthedocs.io/en/latest/django.html#WHITENOISE_STATIC_PREFIX
STATIC_URL = "/static/"
# https://whitenoise.readthedocs.io/en/latest/django.html#make-sure-staticfiles-is-configured-correctly
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

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

# Catalog settings
CATALOGUE_URL = os.environ.get("CATALOGUE_URL")
CATALOGUE_TOKEN = os.environ.get("CATALOGUE_TOKEN")

ENV = os.environ.get("ENV")

DATABASES = {
    "default": {
        "ENGINE": (
            "django.db.backends.postgresql"
            if os.environ.get("RDS_INSTANCE_ADDRESS")
            else "django.db.backends.sqlite3"
        ),
        "NAME": os.environ.get("DATABASE_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("DATABASE_USERNAME", ""),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD", ""),
        "HOST": os.environ.get("RDS_INSTANCE_ADDRESS", ""),
        "PORT": "5432",
    }
}

# Define a service name setting for page titles
SERVICE_NAME = "Find MOJ data"
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

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

ANALYTICS_ID: str = os.environ.get("ANALYTICS_ID", "")
ENABLE_ANALYTICS: bool = (
    os.environ.get("ENABLE_ANALYTICS") in TRUTHY_VALUES
) and ANALYTICS_ID != ""

TESTING = os.environ.get("TESTING") in TRUTHY_VALUES

# Sentry Configuration
if not TESTING:
    sentry_sdk.init(
        dsn=os.environ.get(
            "SENTRY_DSN_WORKAROUND"
        ),  # Datahub overwrites with this variable unless it is renamed,
        # causing Sentry to tag issues with the incorrect environment
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

# Enable / Disable Azure Auth
if not os.environ.get("AZURE_AUTH_ENABLED", "true") == "false":
    # Adds the Azure Authentication middleware to the Django Authentication middleware
    MIDDLEWARE.insert(
        -1,
        "azure_auth.middleware.AzureMiddleware",
    )

    # Azure auth configuration
    AZURE_AUTH = {
        "CLIENT_ID": os.environ.get("AZURE_CLIENT_ID"),
        "CLIENT_SECRET": os.environ.get("AZURE_CLIENT_SECRET"),
        "REDIRECT_URI": os.environ.get("AZURE_REDIRECT_URI"),
        "SCOPES": ["User.Read"],
        "AUTHORITY": os.environ.get("AZURE_AUTHORITY"),
        "PUBLIC_PATHS": [
            "/metrics",
        ],
        "USERNAME_ATTRIBUTE": "mail",
        "USER_MAPPING_FN": "users.helper.user_mapping_fn",
    }
    LOGIN_URL = "/azure_auth/login"
    LOGIN_REDIRECT_URL = "/"  # Or any other endpoint

    AUTHENTICATION_BACKENDS = ("azure_auth.backends.AzureBackend",)

USE_I18N = True
LANGUAGE_CODE = "en"
LOCALE_PATHS = [BASE_DIR / "locale"]
