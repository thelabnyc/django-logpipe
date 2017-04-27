from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


# Make sure settings are installed
try:
    _ = settings.LOGPIPE
except AttributeError as e:
    raise ImproperlyConfigured('Please define `LOGPIPE` in your settings.py file.')


def get(key, default=None):
    if default is None and key not in settings.LOGPIPE:
        raise ImproperlyConfigured('Please ensure LOGPIPE["%s"] is defined in your settings.py file.' % key)
    return settings.LOGPIPE.get(key, default)
