from django.core.exceptions import ImproperlyConfigured
from .constants import FORMAT_JSON, FORMAT_MSGPACK, FORMAT_PICKLE
from .formats.json import JSONRenderer, JSONParser
from .formats.msgpack import MsgPackRenderer, MsgPackParser
from .formats.pickle import PickleRenderer, PickleParser
from .producer import Producer
from .consumer import Consumer, MultiConsumer
from .registry import register_consumer
from . import format, settings
import logging


default_app_config = 'logpipe.config.LogpipeConfig'
logger = logging.getLogger(__name__)


_default_format = settings.get('DEFAULT_FORMAT', FORMAT_JSON)
_allow_incoming_pickle = settings.get('ALLOW_INCOMING_PICKLE', False)
if _default_format == FORMAT_PICKLE:
    if not _allow_incoming_pickle:
        raise ImproperlyConfigured('Can not set DEFAULT_FORMAT to Pickle unless the ALLOW_INCOMING_PICKLE is enabled.')
    logger.warning("DEFAULT_FORMAT is set to Pickle. This is insecure and probable isn't a good idea.")

format.register(FORMAT_JSON, JSONRenderer(), JSONParser())
format.register(FORMAT_MSGPACK, MsgPackRenderer(), MsgPackParser())

if _allow_incoming_pickle:
    format.register(FORMAT_PICKLE, PickleRenderer(), PickleParser())


__all__ = [
    'FORMAT_JSON',
    'FORMAT_MSGPACK',
    'FORMAT_PICKLE',
    'Producer',
    'Consumer',
    'MultiConsumer',
    'register_consumer',
]
