from rest_framework import serializers
from . import models


class PersonSerializer(serializers.ModelSerializer):
    VERSION = 1
    KEY_FIELD = 'uuid'

    class Meta:
        model = models.Person
        fields = ['uuid', 'first_name', 'last_name']


    @classmethod
    def lookup_instance(cls, uuid, **kwargs):
        try:
            person = models.Person.objects.get(uuid=uuid)
            person._disable_kafka_signals = True
            return person
        except models.Person.DoesNotExist:
            pass
