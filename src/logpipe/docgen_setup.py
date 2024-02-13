import os
import sys

docs_dir, _ = os.path.split(__file__)
sys.path.append(os.path.dirname(docs_dir))

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure")
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
]

STATIC_URL = "docgen-static/"

LOGPIPE = {
    "OFFSET_BACKEND": "logpipe.backend.dummy.ModelOffsetStore",
    "PRODUCER_BACKEND": "logpipe.backend.dummy.Producer",
    "CONSUMER_BACKEND": "logpipe.backend.dummy.Consumer",
}

setup = None
from django.apps import apps  # noqa
from django.conf import settings  # noqa
import django  # noqa

if not apps.ready and not settings.configured:
    django.setup()
