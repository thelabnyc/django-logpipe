from typing import Any

from rest_framework import serializers

from logpipe.abc import DRFSerializer

from . import models


class PersonSerializer(
    serializers.ModelSerializer[models.Person],
    DRFSerializer[models.Person],
):
    VERSION = 1
    KEY_FIELD = "uuid"

    class Meta:
        model = models.Person
        fields = ["uuid", "first_name", "last_name"]

    @classmethod
    def lookup_instance(cls, **kwargs: Any) -> models.Person | None:
        uuid = kwargs.get("uuid")
        if uuid is None:
            return None
        try:
            person = models.Person.objects.get(uuid=uuid)
            person._disable_kafka_signals = True
            return person
        except models.Person.DoesNotExist:
            pass
        return None
