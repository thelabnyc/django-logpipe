from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


# Make sure settings are installed
try:
    _ = settings.KAFKA
except AttributeError as e:
    raise ImproperlyConfigured('Please define `KAFKA` in your settings.py file.')


def get(key, default=None):
    if default is None and key not in settings.KAFKA:
        raise ImproperlyConfigured('Please ensure KAFKA["%s"] is defined in your settings.py file.' % key)
    return settings.KAFKA.get(key, default)
