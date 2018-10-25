from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import os


# Make sure settings are installed
try:
    _ = settings.LOGPIPE
except AttributeError:
    raise ImproperlyConfigured('Please define `LOGPIPE` in your settings.py file.')


def get(key, default=None):
    if default is None and key not in settings.LOGPIPE:
        raise ImproperlyConfigured('Please ensure LOGPIPE["%s"] is defined in your settings.py file.' % key)
    return settings.LOGPIPE.get(key, default)


def get_aws_region(_default='us-east-1'):
    # Try to use the explicit KINESIS_REGION setting
    region = get('KINESIS_REGION', '')
    if region:
        return region
    # Try to import boto3 to get the region name
    try:
        import boto3
    except ImportError:
        # Can't import boto3, so fallback to the AWS_DEFAULT_REGION environment variable, then finally, us-east-1
        return os.environ.get('AWS_DEFAULT_REGION', _default)
    # Use the region for boto3's default session
    if boto3.DEFAULT_SESSION is not None:
        region = boto3.DEFAULT_SESSION.region_name
        if region:
            return region
    # Finally, make a new session and use it's region
    region = boto3.session.Session().region_name
    if region:
        return region
    # Finally, return the default
    return _default
