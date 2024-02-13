# Usage Guide

Usage of django-logpipe differs slightly based on if you choose to use [django-rest-framework (DRF)](https://www.django-rest-framework.org/) serializers or [Pydandic](https://docs.pydantic.dev) serializers. Continue reading to see how to handle each case.

## Serializers

### DRF Serializers

The first step in either sending or receiving messages with `logpipe` is to define a serializer. Serializers for `logpipe` have a few rules:

1. Must be either a subclass of `rest_framework.serializers.Serializer` or a class implementing an interface that mimics `rest_framework.serializers.Serializer`.
1. Must have a `MESSAGE_TYPE` attribute defined on the class. The value should be a string that defines uniquely defines the data-type within it's Topic / Stream.
2. Must have a `VERSION` attribute defined on the class. The value should be a monotonic integer representing the schema version number.
3. Must have a `KEY_FIELD` attribute defined on the class, representing the name of the field to use as the message key. The message key is used by Kafka when performing log compaction and by Kinesis as the shard partition key. The property can be omitted for topics which do not require a key.
4. If the serializer will be used for incoming-messages, it should implement class method `lookup_instance(cls, **kwargs)`. This class method will be called with message data as keyword arguments directly before instantiating the serializer. It should lookup and return the related object (if one exists) so that it can be passed to the serializer's `instance` argument during initialization. If no object exists yet (the message is representing a new object), it should return `None`.

Below is a sample Django model and it's accompanying serializer.

```py title="myapp/models.py"
from django.db import models
from rest_framework import serializers
import uuid


class Person(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)


class PersonSerializer(serializers.ModelSerializer):
    MESSAGE_TYPE = 'person'
    VERSION = 1
    KEY_FIELD = 'uuid'

    class Meta:
        model = Person
        fields = ['uuid', 'first_name', 'last_name']

    @classmethod
    def lookup_instance(cls, uuid, **kwargs):
        try:
            return Person.objects.get(uuid=uuid)
        except models.Person.DoesNotExist:
            pass
```

### Pydantic Serializers

As an alternative to using DRF serializers (as described above), you may also use Pydantic models. The same `MESSAGE_TYPE`, `VERSION`, `KEY_FIELD` must be defined as `ClassVar`s on the model class.

```py title="myapp/models.py"
from typing import ClassVar
from django.db import models
from logpipe.abc import PydanticModel
import uuid


class Person(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)


class PersonSchema(PydanticModel):
    MESSAGE_TYPE: ClassVar[str] = 'person'
    VERSION: ClassVar[int] = 1
    KEY_FIELD: ClassVar[str] = 'uuid'

    uuid: uuid.UUID
    first_name: str
    last_name: str

    def save(self) -> Person:
        """
        The save method is called when a `person` message is consumed from the
        data stream.
        """
        try:
            person = Person.objects.get(uuid=self.uuid)
        except Person.DoesNotExist:
            person = Person()
        person.first_name = self.first_name
        person.last_name = self.last_name
        person.save()
        return person
```

## Sending Messages

### DRF Producer

Once a serializer exists, you can send a message to Kafka by creating Producer object and calling the `send` method.

```py
from logpipe import DRFProducer
from .models import Person, PersonSerializer

joe = Person.objects.create(
    first_name='Joe',
    last_name='Schmoe',
)
producer = DRFProducer('people', PersonSerializer)
producer.send(joe)
```

The above sample code would result in the following message being sent to the Kafka topic named `people`.

```txt
json:{"type":"person","version":1,"producer":"my-application-name","message":{"first_name":"Joe","last_name":"Schmoe","uuid":"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"}}
```

### Pydantic Producer

If using a Pydantic model instead of a DRF serializer, use the `PydanticProducer` class instead of `DRFProducer`.

```py
from logpipe import PydanticProducer
from .models import PersonSchema
import uuid

joe = PersonSchema(
    uuid=uuid.uuid4(),
    first_name='Joe',
    last_name='Schmoe',
)
producer = PydanticProducer('people')
producer.send(joe)
```

The above sample code would result in the following message being sent to the Kafka topic named `people`.

```txt
json:{"type":"person","version":1,"producer":"my-application-name","message":{"first_name":"Joe","last_name":"Schmoe","uuid":"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"}}
```

## Receiving Messages

To processing incoming messages, we can reuse the same model and serializer. We just need to instantiate a Consumer object. Unlike Producers, there's not separate Consumer classes for DRF vs. Pydantic serializers. Either type of serializer can be passed into the `Consumer.register` method.

```py
from logpipe import Consumer
from .models import PersonSerializer, PersonSchema

# Watch for messages, but timeout after 1000ms of no messages
consumer = Consumer('people', consumer_timeout_ms=1000)
consumer.register(PersonSerializer)
consumer.run()

# Watch for messages and block forever
consumer = Consumer('people')
consumer.register(PersonSerializer)
consumer.run()

# Pydantic serializers work here too.
consumer = Consumer('people')
consumer.register(PersonSchema)
consumer.run()
```

The consumer object uses Django REST Framework's built-in `save`, `create`, and `update` methods to apply the message. If your messages aren't tied directly to a Django model, skip defining the `lookup_instance` class method and override the `save` method to house your custom import logic.

### Consuming Multiple Data-Types Per Topic

If you have multiple data-types in a single topic or stream, you can consume them all by registering multiple serializers with the consumer.

```py
from logpipe import Consumer
from .models import PersonSerializer, PlaceSerializer, ThingSerializer

consumer = Consumer('nouns')
consumer.register(PersonSerializer)
consumer.register(PlaceSerializer)
consumer.register(ThingSerializer)
consumer.run()
```

You can also support multiple incompatible version of message types by defining a serializer for each message type version and registering them all with the consumer.

```py
from logpipe import Consumer
from .models import (
    PersonSerializerVersion1,
    PersonSerializerVersion2,
    PlaceSerializer,
    ThingSerializer,
)

consumer = Consumer('nouns')
consumer.register(PersonSerializerVersion1)
consumer.register(PersonSerializerVersion2)
consumer.register(PlaceSerializer)
consumer.register(ThingSerializer)
consumer.run()
```

### Consuming from Multiple Topics

If you have multiple streams or topics to watch, make a consumers for each, and watch them all simultaneously in the same process by using a MultiConsumer.

```py
from logpipe import MultiConsumer, Consumer
from .models import (
    PersonSerializer,
    PlaceSerializer,
)

people_consumer = Consumer('people')
people_consumer.register(PersonSerializer)

places_consumer = Consumer('places')
places_consumer.register(PlaceSerializer)

multi = MultiConsumer(people_consumer, places_consumer)

# Watch for 'people' and 'places' topics indefinitely
multi.run()
```

### Management Commands

Finally, consumers can be registered and run automatically by the build in `run_kafka_consumer` management command.

```py
# myapp/apps.py
from django.apps import AppConfig
from logpipe import Consumer, register_consumer

class MyAppConfig(AppConfig):
    name = 'myapp'

# Register consumers with logpipe
@register_consumer
def build_person_consumer():
    consumer = Consumer('people')
    consumer.register(PersonSerializer)
    return consumer
```

Use the `register_consumer` decorator to register as many consumers and topics as you need to work with. Then, run the `run_kafka_consumer` command to process messages for all consumers automatically in a round-robin fashion.

```py
python manage.py run_kafka_consumer
```


## Dealing with Schema Changes

Schema changes are handled using the `VERSION` attribute required on every serializer class. When sending, a producer includes the schema version number in the message data. Then, when a consumer receives a message, it looks for a register serializer with a matching version number. If no serializer is found with a matching version number, a `logpipe.exceptions.UnknownMessageVersionError` exception is raised.

To perform a backwards-incompatible schema change, the following steps should be performed.

1. Update consumer code to have knowledge of the new schema version.
2. Update producer code to being sending the new schema version.
3. After some amount of time (when you are sure no old-version messages still exist in Kafka), remove the code related to the old schema version.

For example, if we wanted to require an email field on the `Person` model we defined above, the first step would be to update consumers to know about the new field.

```py
class Person(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, null=True)


class PersonSerializerV1(serializers.ModelSerializer):
    MESSAGE_TYPE = 'person'
    VERSION = 1
    KEY_FIELD = 'uuid'

    class Meta:
        model = Person
        fields = ['uuid', 'first_name', 'last_name']


class PersonSerializerV2(PersonSerializerV1):
    MESSAGE_TYPE = 'person'
    VERSION = 2

    class Meta(PersonSerializerV1.META):
        fields = ['uuid', 'first_name', 'last_name', 'email']


consumer = Consumer('people', consumer_timeout_ms=1000)
consumer.register(PersonSerializerV1)
consumer.register(PersonSerializerV2)
```

The consumers will now use the appropriate serializer for the message version. Second, we need to update producer code to being using schema version 2.

```py
producer = Producer('people', PersonSerializerV2)
```

Finally, after all the old version 1 messages have been dropped (by log compaction), the `PersonSerializerV1` class can be removed form the code base.
