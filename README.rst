===============================
Django LogPipe
===============================

|  |build| |license| |kit| |format| |downloads|

This library serves as a universal pipe for moving data around between Django applications and services. It is build on
top of `Apache Kafka`_, `kafka-python`_, and `Django REST Framework`_.

.. _`Apache Kafka`: https://kafka.apache.org/
.. _`kafka-python`: https://github.com/dpkp/kafka-python
.. _`Django REST Framework`: http://www.django-rest-framework.org/


Installation
============

Install `django-logpipe` from pip.::

    $ pip install django-logpipe

Add `logpipe` to your installed apps.::

    INSTALLED_APPS = [
        ...
        'logpipe',
        ...
    ]

Add connection settings to your `settings.py` file.::

    KAFKA = {
        'BOOTSTRAP_SERVERS': [
            'kafka:9092'
        ],
    }

Run migrations. This will create the model used to store Kafka log position offsets.::

    $ python manage.py migrate logpipe

Usage
=====

Serializers
-----------

The first step in either sending or receiving messages with `logpipe` is to define a serializer. Serializers for `logpipe` have a few rules:

1. Must be either a subclass of `rest_framework.serializers.Serializer` or a class implementing an interface that mimics `rest_framework.serializers.Serializer`.
2. Must have property `VERSION` defined on the class, representing the schema version number.
3. Should have property `KEY_FIELD` defined on the class, representing the name of the field to use as the message key. The message key is used by Kafka when performing log compaction. The property can be omitted for topics which do not require a key.
4. If the serializer will be used for incoming-messages, it should implement class method `lookup_instance(cls, **kwargs)`. This class method will be with message data as kwargs directly before instantiating the serializer. It should lookup and return the related object (if one exists) so that it can be passed to the serializer's `instance` argument during initialization. If not objects exists yet (the message is representing a new object), it should return `None`.

Below is a sample Django model and it's accompanying serializer.::


    from django.db import models
    from rest_framework import serializers
    import uuid

    class Person(models.Model):
        uuid = models.UUIDField(default=uuid.uuid4, unique=True)
        first_name = models.CharField(max_length=200)
        last_name = models.CharField(max_length=200)

    class PersonSerializer(serializers.ModelSerializer):
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


Sending Messages
----------------

Once a serializer exists, you can send a message to Kafka by creating Producer object and calling the `send` method.::

    from logpipe import Producer
    joe = Person.objects.create(first_name='Joe', last_name='Schmoe')
    producer = Producer('people', PersonSerializer)
    producer.send(joe)

The above sample code would result in the following message being sent to the Kafka topic named `people`.::

    json:{"version":1,"message":{"first_name":"Joe","last_name":"Schmoe","uuid":"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"}}


Receiving Messages
------------------

To processing incoming messages, we can reuse the same model and serializer. We just need to instantiate a Consumer object.::

    # Watch for messages, but timeout after 1000ms of no messages
    consumer = Consumer('people', consumer_timeout_ms=1000)
    consumer.register(PersonSerializer)
    consumer.run()

    # Watch for messages and block forever
    consumer = Consumer('people')
    consumer.register(PersonSerializer)
    consumer.run()

The consumer object uses Django REST Framework's built-in `save`, `create`, and `update` methods to apply the message. If your messages are tied directly to a Django model, skip defining the `lookup_instance` class method and override the `save` method to house your custom import logic.

Multiple consumers can be watched simultaneously by the same process by using a MultiConsumer.::

    from logpipe import MultiConsumer
    people_consumer = Consumer('people')
    people_consumer.register(PersonSerializer)
    places_consumer = Consumer('places')
    places_consumer.register(PlaceSerializer)
    multi = MultiConsumer(people_consumer, places_consumer)

    # Watch for 'people' and 'places' topics indefinitely
    multi.run()

Finally, consumers can be registered and run automatically by the build in `run_kafka_consumer` management command.::

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

Use the `register_consumer` decorator to register as many consumers and topics as you need to work with. Then, run the `run_kafka_consumer` command to process messages for all consumers automatically in a round-robin fashion.::

    $ python manage.py run_kafka_consumer


Dealing with Schema Changes
---------------------------

Schema changes are handled using the `VERSION` attribute required on every serializer class. When sending, a producer includes the schema version number in the message data. Then, when a consumer receives a message, it looks for a register serializer with a matching version number. If no serializer is found with a matching version number, a `logpipe.exceptions.UnknownMessageVersionError` exception is raised.

To perform a backwards-incompatible schema change, the following steps should be performed.

1. Update consumer code to have knowledge of the new schema version.
2. Update producer code to being sending the new schema version.
3. After some amount of time (when you are sure no old-version messages still exist in Kafka), remove the code related to the old schema version.

For example, if we wanted to require an email field on the `Person` model we defined above, the first step would be to update consumers to know about the new field.::


    class Person(models.Model):
        uuid = models.UUIDField(default=uuid.uuid4, unique=True)
        first_name = models.CharField(max_length=200)
        last_name = models.CharField(max_length=200)
        email = models.EmailField(max_length=200, null=True)

    class PersonSerializerV1(serializers.ModelSerializer):
        VERSION = 1
        KEY_FIELD = 'uuid'
        class Meta:
            model = Person
            fields = ['uuid', 'first_name', 'last_name']

    class PersonSerializerV2(PersonSerializerV1):
        VERSION = 2
        class Meta(PersonSerializerV1.META):
            fields = ['uuid', 'first_name', 'last_name', 'email']

    consumer = Consumer('people', consumer_timeout_ms=1000)
    consumer.register(PersonSerializerV1)
    consumer.register(PersonSerializerV2)

The consumers will now use the appropriate serializer for the message version. Second, we need to update producer code to being using schema version 2.::

    producer = Producer('people', PersonSerializerV2)

Finally, after all the old version 1 messages have been dropped (by log compaction), the `PersonSerializerV1` class can be removed form the code base.


Settings
========

The follow settings added to `settings.py` to configure `logpipe`.

+--------------------+----------------------------------------------------------------------+------------------------------------------+
| Key                | Description                                                          | Default Value                            |
+====================+======================================================================+==========================================+
| BOOTSTRAP_SERVERS  | A list of Kafka servers to connect to upon startup.                  | *Required*                               |
+--------------------+----------------------------------------------------------------------+------------------------------------------+
| DEFAULT_FORMAT     | The default serialization format to use when sending new messages.   | json                                     |
+--------------------+----------------------------------------------------------------------+------------------------------------------+
| OFFSET_BACKEND     | Path to class used to store offset data.                             | logpipe.offset_backends.ModelOffsetStore |
+--------------------+----------------------------------------------------------------------+------------------------------------------+
| MIN_MESSAGE_LAG_MS | Minimum amount of time between when a message is sent and when it    |                                          |
|                    | will be processed. This is useful is a single service is both        | 500                                      |
|                    | producing and consuming the same topic.                              |                                          |
+--------------------+----------------------------------------------------------------------+------------------------------------------+
| RETRIES            | Number of times to retry sending a message.                          | 0                                        |
+--------------------+----------------------------------------------------------------------+------------------------------------------+
| TIMEOUT            | How many seconds to wait for a message sent confirmation from Kafka. | 10                                       |
+--------------------+----------------------------------------------------------------------+------------------------------------------+


Changelog
=========

0.1.0
------------------
- Initial release.


.. |build| image:: https://gitlab.com/thelabnyc/django-logpipe/badges/master/build.svg
    :target: https://gitlab.com/thelabnyc/django-logpipe/commits/master
.. |license| image:: https://img.shields.io/pypi/l/django-logpipe.svg
    :target: https://pypi.python.org/pypi/
.. |kit| image:: https://badge.fury.io/py/django-logpipe.svg
    :target: https://pypi.python.org/pypi/django-logpipe
.. |format| image:: https://img.shields.io/pypi/format/django-logpipe.svg
    :target: https://pypi.python.org/pypi/django-logpipe
.. |downloads| image:: https://img.shields.io/pypi/dm/django-logpipe.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/django-logpipe
