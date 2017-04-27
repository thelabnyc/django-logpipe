from django.apps import apps
from django.utils.module_loading import import_string
from . import settings
import kafka
import logging


logger = logging.getLogger(__name__)


class ModelOffsetStore(object):
    def commit(self, client, message):
        KafkaOffset = apps.get_model(app_label='logpipe', model_name='KafkaOffset')
        logger.info('Commit offset "%s" for topic "%s", partition "%s" to %s' % (
            message.offset, message.topic, message.partition, self.__class__.__name__))
        obj, created = KafkaOffset.objects.get_or_create(
            topic=message.topic,
            partition=message.partition)
        obj.offset = message.offset + 1
        obj.save()


    def seek(self, client, topic, partition):
        KafkaOffset = apps.get_model(app_label='logpipe', model_name='KafkaOffset')
        tp = kafka.TopicPartition(topic=topic, partition=partition)
        try:
            obj = KafkaOffset.objects.get(topic=topic, partition=partition)
            logger.info('Seeking to offset "%s" on topic "%s", partition "%s"' % (obj.offset, topic, partition))
            client.seek(tp, obj.offset)
        except KafkaOffset.DoesNotExist:
            logger.info('Seeking to beginning of topic "%s", partition "%s"' % (topic, partition))
            client.seek_to_beginning(tp)


class KafkaOffsetStore(object):
    def commit(self, client, message):
        logger.info('Commit offset "%s" for topic "%s", partition "%s" to %s' % (
            message.offset, message.topic, message.partition, self.__class__.__name__))
        client.commit()

    def seek(self, client, topic, partition):
        pass



def get_backend():
    default = 'logpipe.offset_backends.ModelOffsetStore'
    backend_path = settings.get('OFFSET_BACKEND', default)
    return import_string(backend_path)()
