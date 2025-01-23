from typing import Any

from django.dispatch import receiver

from logpipe import Producer

from . import constants, models, serializers, signals


@receiver(
    signals.person_altered,
    sender=models.Person,
    dispatch_uid="send_person_altered_message",
)
def send_person_altered_message(
    sender: type[models.Person],
    person: models.Person,
    **kwargs: Any,
) -> None:
    producer = Producer(constants.TOPIC_PEOPLE, serializers.PersonSerializer)
    producer.send(person)
