import os

from django.utils.translation import gettext_lazy as _
import django_stubs_ext

django_stubs_ext.monkeypatch()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True
SECRET_KEY = "li0$-gnv)76g$yf7p@(cg-^_q7j6df5cx$o-gsef5hd68phj!4"
SITE_ID = 1
ROOT_URLCONF = "sandbox.urls"
ALLOWED_HOSTS = ["*"]

USE_I18N = True
LANGUAGE_CODE = "en-us"
LANGUAGES = (
    ("en-us", _("English")),
    ("es", _("Spanish")),
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.flatpages",
    "logpipe",
    "sandbox.lptester",
]

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
)

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "postgres",
        "PORT": 5432,
    }
}


STATIC_URL = "/static/"


LOGPIPE = {
    "KAFKA_BOOTSTRAP_SERVERS": ["spotify__kafka:9092"],
    "KAFKA_CONSUMER_KWARGS": {
        "group_id": "django-logpipe",
    },
    # OFFSET_BACKEND: Defaults to logpipe.backend.kafka.ModelOffsetStore.
    # CONSUMER_BACKEND: Defaults to logpipe.backend.kafka.Consumer.
    # PRODUCER_BACKEND: Defaults to logpipe.backend.kafka.Producer.
    # KAFKA_BOOTSTRAP_SERVERS: List of Kafka hostname:post pairs. Required when using Kafka.
    # KAFKA_SEND_TIMEOUT: Defaults to 10 seconds.
    # KAFKA_MAX_SEND_RETRIES: Defaults to 0 retry attempts.
    # KINESIS_REGION: Defaults to 'us-east-1'.
    # KINESIS_FETCH_LIMIT: Defaults to 25 records.
    # KINESIS_SEQ_NUM_CACHE_SIZE: Defaults to 1000.
    # MIN_MESSAGE_LAG_MS: Defaults to 0ms
    # DEFAULT_FORMAT: Defaults to 'json'
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s django %(name)s: %(levelname)s %(process)d %(thread)d %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "verbose"}},
    "loggers": {
        "logpipe": {
            "level": "CRITICAL",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "CRITICAL",
    },
}
