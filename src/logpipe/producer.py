from .backend import get_producer_backend
from .constants import FORMAT_JSON
from .format import render
from . import settings
import logging


logger = logging.getLogger(__name__)


class Producer(object):
    _client = None

    def __init__(self, topic_name, serializer_class):
        self.client = get_producer_backend()
        self.topic_name = topic_name
        self.serializer_class = serializer_class


    def send(self, data, renderer=None):
        if hasattr(data, '__dict__'):
            data = data.__dict__

        instance = None
        if hasattr(self.serializer_class, 'lookup_instance'):
            instance = self.serializer_class.lookup_instance(**data)
        ser = self.serializer_class(instance=instance, data=data)
        ser.is_valid(raise_exception=True)

        message_type = getattr(self.serializer_class, 'MESSAGE_TYPE', None)
        if not message_type:
            raise AttributeError('You must define a MESSAGE_TYPE attribute on the serializer class')

        key_field = getattr(self.serializer_class, 'KEY_FIELD', None)
        key = None
        if key_field:
            key = str(ser.validated_data[key_field])

        renderer = settings.get('DEFAULT_FORMAT', FORMAT_JSON)
        body = {
            'type': message_type,
            'version': self.serializer_class.VERSION,
            'message': ser.validated_data,
        }
        serialized_data = render(renderer, body)

        record_metadata = self.client.send(self.topic_name, key=key, value=serialized_data)
        logger.debug('Sent message with type "%s", key "%s" to topic "%s"' % (message_type, key, self.topic_name))
        return record_metadata
