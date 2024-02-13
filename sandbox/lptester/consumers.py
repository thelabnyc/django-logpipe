from logpipe import Consumer, register_consumer

from . import constants, serializers


@register_consumer
def build_person_consumer():
    consumer = Consumer(constants.TOPIC_PEOPLE)
    consumer.register(serializers.PersonSerializer)
    return consumer
