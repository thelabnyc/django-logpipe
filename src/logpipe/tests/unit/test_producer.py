from unittest import mock

from django.test import TestCase
from pydantic import computed_field
from rest_framework import serializers

from logpipe import DRFProducer, PydanticProducer
from logpipe.tests.common import (
    TOPIC_STATES,
    State_Pydantic,
    StateModel,
    StateSerializer_DRF,
)


class CustomStateSerializer_DRF(StateSerializer_DRF):
    my_ser_method_field = serializers.SerializerMethodField()

    def get_my_ser_method_field(self, obj):
        return f"value-{obj.code}"


class CustomState_Pydantic(State_Pydantic):
    @computed_field
    def my_ser_method_field(self) -> str:
        return f"value-{self.code}"


class DRFProducerTest(TestCase):
    def test_send_serializer_method_field(self):
        fake_client = mock.MagicMock()
        fake_client.send = mock.MagicMock()

        def check_args(topic, key, value):
            self.assertEqual(topic, TOPIC_STATES)
            self.assertEqual(key, "NY")
            self.assertJSONEqual(
                value.decode().replace("json:", ""),
                {
                    "type": "us-state",
                    "version": 1,
                    "message": {
                        "code": "NY",
                        "name": "New York",
                        "my_ser_method_field": "value-NY",
                    },
                },
            )

        fake_client.send.side_effect = check_args

        get_producer_backend = mock.MagicMock()
        get_producer_backend.return_value = fake_client

        with mock.patch("logpipe.producer.get_producer_backend", get_producer_backend):
            producer = DRFProducer(TOPIC_STATES, CustomStateSerializer_DRF)

        ny = StateModel(
            id=5,
            code="NY",
            name="New York",
        )
        producer.send(ny)

        self.assertEqual(fake_client.send.call_count, 1)

    def test_send_with_producer_id(self):
        fake_client = mock.MagicMock()
        fake_client.send = mock.MagicMock()

        def check_args(topic, key, value):
            self.assertEqual(topic, TOPIC_STATES)
            self.assertEqual(key, "NY")
            self.assertJSONEqual(
                value.decode().replace("json:", ""),
                {
                    "type": "us-state",
                    "version": 1,
                    "producer": "my-producer-app",
                    "message": {
                        "code": "NY",
                        "name": "New York",
                        "my_ser_method_field": "value-NY",
                    },
                },
            )

        fake_client.send.side_effect = check_args

        get_producer_backend = mock.MagicMock()
        get_producer_backend.return_value = fake_client

        with mock.patch("logpipe.producer.get_producer_backend", get_producer_backend):
            producer = DRFProducer(
                TOPIC_STATES,
                CustomStateSerializer_DRF,
                producer_id="my-producer-app",
            )

        ny = StateModel(
            id=5,
            code="NY",
            name="New York",
        )
        producer.send(ny)

        self.assertEqual(fake_client.send.call_count, 1)


class PydanticProducerTest(TestCase):
    def test_send_serializer_method_field(self):
        fake_client = mock.MagicMock()
        fake_client.send = mock.MagicMock()

        def check_args(topic, key, value):
            self.assertEqual(topic, TOPIC_STATES)
            self.assertEqual(key, "NY")
            self.assertJSONEqual(
                value.decode().replace("json:", ""),
                {
                    "type": "us-state",
                    "version": 1,
                    "message": {
                        "code": "NY",
                        "name": "New York",
                        "my_ser_method_field": "value-NY",
                    },
                },
            )

        fake_client.send.side_effect = check_args

        get_producer_backend = mock.MagicMock()
        get_producer_backend.return_value = fake_client

        with mock.patch("logpipe.producer.get_producer_backend", get_producer_backend):
            producer = PydanticProducer(TOPIC_STATES)

        ny = CustomState_Pydantic(
            id=5,
            code="NY",
            name="New York",
        )
        producer.send(ny)

        self.assertEqual(fake_client.send.call_count, 1)

    def test_send_with_producer_id(self):
        fake_client = mock.MagicMock()
        fake_client.send = mock.MagicMock()

        def check_args(topic, key, value):
            self.assertEqual(topic, TOPIC_STATES)
            self.assertEqual(key, "NY")
            self.assertJSONEqual(
                value.decode().replace("json:", ""),
                {
                    "type": "us-state",
                    "version": 1,
                    "producer": "my-producer-app",
                    "message": {
                        "code": "NY",
                        "name": "New York",
                        "my_ser_method_field": "value-NY",
                    },
                },
            )

        fake_client.send.side_effect = check_args

        get_producer_backend = mock.MagicMock()
        get_producer_backend.return_value = fake_client

        with mock.patch("logpipe.producer.get_producer_backend", get_producer_backend):
            producer = PydanticProducer(
                TOPIC_STATES,
                producer_id="my-producer-app",
            )

        ny = CustomState_Pydantic(
            id=5,
            code="NY",
            name="New York",
        )
        producer.send(ny)

        self.assertEqual(fake_client.send.call_count, 1)
