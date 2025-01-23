from typing import Any
import uuid

from django.db import models

from .signals import person_altered


class Person(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    _disable_kafka_signals = False

    def save(self, *args: Any, **kwargs: Any) -> None:
        ret = super().save(*args, **kwargs)
        if not self._disable_kafka_signals:
            person_altered.send(sender=self.__class__, person=self)
        return ret
