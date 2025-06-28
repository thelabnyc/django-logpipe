import collections

from django.test import override_settings

from logpipe import Consumer, DRFProducer, MultiConsumer, PydanticProducer
from logpipe.backend.dummy import reset_topics
from logpipe.tests.common import (
    TOPIC_STATES,
    BaseTest,
    State_Pydantic,
    StateModel,
    StateSerializer_DRF,
)

LOGPIPE = {
    "OFFSET_BACKEND": "logpipe.backend.dummy.ModelOffsetStore",
    "PRODUCER_BACKEND": "logpipe.backend.dummy.Producer",
    "CONSUMER_BACKEND": "logpipe.backend.dummy.Consumer",
}


class DRFConsumerTest(BaseTest):
    def setUp(self):
        super().setUp()
        reset_topics()

    @override_settings(LOGPIPE=LOGPIPE)
    def test_normal_consume(self):
        # Send a message to the dummy producer
        producer = DRFProducer(TOPIC_STATES, StateSerializer_DRF)
        ny = StateModel(
            id=5,
            code="NY",
            name="New York",
        )
        producer.send(ny)

        # Setup the consumer serializer
        test = collections.Counter()

        def save(ser):
            self.assertEqual(ser.validated_data["code"], "NY")
            self.assertEqual(ser.validated_data["name"], "New York")
            test["i"] += 1

        FakeStateSerializer = self.mock_state_serializer_drf(save)

        # Retrieve the message from the dummy consumer.
        consumer = Consumer(TOPIC_STATES)
        consumer.register(FakeStateSerializer)

        consumer.run(iter_limit=10)
        self.assertEqual(self.serializers["state"].save.call_count, 1)

        # Not called again
        consumer.run(iter_limit=10)
        self.assertEqual(self.serializers["state"].save.call_count, 1)
        self.assertEqual(test["i"], 1)


class PydanticConsumerTest(BaseTest):
    def setUp(self):
        super().setUp()
        reset_topics()

    @override_settings(LOGPIPE=LOGPIPE)
    def test_normal_consume(self):
        # Send a message to the dummy producer
        producer = PydanticProducer(TOPIC_STATES)
        ny = State_Pydantic(
            id=5,
            code="NY",
            name="New York",
        )
        producer.send(ny)

        # Setup the consumer serializer
        test = collections.Counter()

        def save(_self):
            self.assertEqual(_self._instance, None)
            self.assertEqual(_self.code, "NY")
            self.assertEqual(_self.name, "New York")
            test["i"] += 1

        FakeStateSerializer = self.mock_state_serializer_pydantic(save)

        # Retrieve the message from the dummy consumer.
        consumer = Consumer(TOPIC_STATES)
        consumer.register(FakeStateSerializer)

        # Save called once.
        consumer.run(iter_limit=10)
        self.assertEqual(test["i"], 1)

        # Not called again
        consumer.run(iter_limit=10)
        self.assertEqual(test["i"], 1)


class MultiConsumerTest(BaseTest):
    def setUp(self):
        super().setUp()
        reset_topics()

    @override_settings(LOGPIPE=LOGPIPE)
    def test_normal_consume(self):
        # Send a message to the dummy producer
        producer = PydanticProducer(TOPIC_STATES)
        ny = State_Pydantic(
            id=5,
            code="NY",
            name="New York",
        )
        for i in range(5):
            producer.send(ny)

        # Setup the consumer serializer
        test = collections.Counter()

        def save(_self):
            self.assertEqual(_self._instance, None)
            self.assertEqual(_self.code, "NY")
            self.assertEqual(_self.name, "New York")
            test["i"] += 1

        FakeStateSerializer = self.mock_state_serializer_pydantic(save)

        # Retrieve the message from the dummy consumer.
        inner_consumer = Consumer(TOPIC_STATES)
        inner_consumer.register(FakeStateSerializer)
        consumer = MultiConsumer(inner_consumer, inner_consumer)

        # Save called once.
        consumer.run(iter_limit=10)
        self.assertEqual(test["i"], 5)
