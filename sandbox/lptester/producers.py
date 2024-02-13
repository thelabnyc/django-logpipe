from django.dispatch import receiver

from logpipe import Producer

from . import constants, models, serializers, signals


@receiver(
    signals.person_altered,
    sender=models.Person,
    dispatch_uid="send_person_altered_message",
)
def send_person_altered_message(sender, person, **kwargs):
    producer = Producer(constants.TOPIC_PEOPLE, serializers.PersonSerializer)
    producer.send(person)
