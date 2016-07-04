from .constants import FORMAT_JSON
from .format import render
from . import settings
import kafka
import logging


logger = logging.getLogger(__name__)


class Producer(object):
    _client = None

    def __init__(self, topic_name, serializer_class):
        self.topic_name = topic_name
        self.serializer_class = serializer_class


    @property
    def client(self):
        if not self._client:
            kwargs = self._get_client_config()
            self._client = kafka.KafkaProducer(**kwargs)
        return self._client


    def send(self, data, renderer=None):
        if hasattr(data, '__dict__'):
            data = data.__dict__

        instance = None
        if hasattr(self.serializer_class, 'lookup_instance'):
            instance = self.serializer_class.lookup_instance(**data)
        ser = self.serializer_class(instance=instance, data=data)
        ser.is_valid(raise_exception=True)

        key_field = getattr(self.serializer_class, 'KEY_FIELD', None)
        key = None
        if key_field:
            key = str(ser.validated_data[key_field]).encode()

        renderer = settings.get('DEFAULT_FORMAT', FORMAT_JSON)
        body = {
            'version': self.serializer_class.VERSION,
            'message': ser.validated_data,
        }
        serialized_data = render(renderer, body)

        timeout = settings.get('TIMEOUT', 10)
        future = self.client.send(self.topic_name, key=key, value=serialized_data)
        record_metadata = future.get(timeout=timeout)
        logger.info('Sent message with key "%s" to topic "%s"' % (key.decode(), self.topic_name))
        return record_metadata


    def _get_client_config(self):
        servers = settings.get('BOOTSTRAP_SERVERS')
        retries = settings.get('RETRIES', 0)
        return {
            'bootstrap_servers': servers,
            'retries': retries,
        }
