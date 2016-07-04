from django.db import transaction
from .exceptions import InvalidMessageError, UnknownMessageVersionError, MissingTopicError
from .offset_backends import get_backend
from .format import parse
from . import settings
import itertools
import kafka
import logging
import time


logger = logging.getLogger(__name__)


class Consumer(object):
    _client = None

    def __init__(self, topic_name, **kwargs):
        self.topic_name = topic_name
        self.client_kwargs = kwargs
        self.serializer_classes = {}


    @property
    def client(self):
        if not self._client:
            kwargs = self._get_client_config()
            self._client = kafka.KafkaConsumer(**kwargs)
            tps = self._get_topic_partitions()
            self._client.assign(tps)
            backend = get_backend()
            for tp in tps:
                backend.seek(self._client, tp.topic, tp.partition)
        return self._client


    def commit(self, message):
        get_backend().commit(self.client, message)


    def register(self, serializer_class):
        v = serializer_class.VERSION
        self.serializer_classes[v] = serializer_class


    def run(self, iter_limit=0):
        i = 0
        for message, serializer in self:
            with transaction.atomic():
                serializer.save()
                self.commit(message)
            i += 1
            if iter_limit > 0 and i >= iter_limit:
                break


    def __iter__(self):
        return self


    def __next__(self):
        message = next(self.client)
        # ConsumerRecord(topic='', partition=0, offset=0, timestamp=1467649216540, timestamp_type=0, key=b'', value=b'')
        info = (message.key.decode(), message.topic, message.partition, message.offset)
        logger.info('Received message with key "%s" from topic "%s", partition "%s", offset "%s"' % info)

        # Wait?
        lag_ms = (time.time() * 1000) - message.timestamp
        logger.info("Message lag is %sms" % lag_ms)
        wait_ms = settings.get('MIN_MESSAGE_LAG_MS', 500) - lag_ms
        if wait_ms > 0:
            logger.info("Respecting MIN_MESSAGE_LAG_MS by waiting %sms" % wait_ms)
            time.sleep(wait_ms / 1000)
            logger.info("Finished waiting")

        serializer = self._unserialize(message)
        return message, serializer


    def __str__(self):
        return '<logpipe.consumer.Consumer topic="%s">' % self.topic_name


    def _unserialize(self, message):
        data = parse(message.value)
        if 'version' not in data:
            raise InvalidMessageError('Received message missing missing a top-level "version" key.')
        if 'message' not in data:
            raise InvalidMessageError('Received message missing missing a top-level "message" key.')

        version = data['version']
        if version not in self.serializer_classes:
            raise UnknownMessageVersionError('Received message with unknown version "%s" in topic %s' % (version, message.topic))

        serializer_class = self.serializer_classes[version]

        instance = None
        if hasattr(serializer_class, 'lookup_instance'):
            instance = serializer_class.lookup_instance(**data['message'])
        serializer = serializer_class(instance=instance, data=data['message'])
        serializer.is_valid(raise_exception=True)
        return serializer


    def _get_topic_partitions(self):
        p = []
        partitions = self.client.partitions_for_topic(self.topic_name)
        if not partitions:
            raise MissingTopicError('Could not find topic %s. Does it exist?' % self.topic_name)
        for partition in partitions:
            tp = kafka.TopicPartition(self.topic_name, partition=partition)
            p.append(tp)
        return p


    def _get_client_config(self):
        kwargs = {
            'auto_offset_reset': 'earliest',
            'enable_auto_commit': False,
            'consumer_timeout_ms': 1000,
        }
        kwargs.update(self.client_kwargs)
        kwargs.update({
            'bootstrap_servers': settings.get('BOOTSTRAP_SERVERS'),
        })
        return kwargs


class MultiConsumer(object):
    def __init__(self, *consumers):
        self.consumers = consumers

    def run(self):
        for consumer in itertools.cycle(self.consumers):
            consumer.run(iter_limit=1)
