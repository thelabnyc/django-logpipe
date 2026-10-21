from django.conf import settings
from django.test import override_settings

from logpipe import Consumer, Producer

from ..common import TOPIC_STATES, BaseTest, StateSerializer_DRF


class RoundTripTest(BaseTest):
    def test_roundtrip_state(self):
        def save(ser):
            self.assertEqual(ser.validated_data["code"], "NY")
            self.assertEqual(ser.validated_data["name"], "New York")

        FakeStateSerializer = self.mock_state_serializer_drf(save)

        producer = Producer(TOPIC_STATES, StateSerializer_DRF)
        record = producer.send({"code": "NY", "name": "New York"})
        self.assertEqual(record.topic, "us-states")
        self.assertEqual(record.partition, 0)
        self.assertTrue(record.offset >= 0)

        # producer.client.flush()

        with Consumer(TOPIC_STATES, consumer_timeout_ms=1000) as consumer:
            consumer.register(FakeStateSerializer)
            consumer.run(iter_limit=1)

        self.assertEqual(FakeStateSerializer.call_count, 1)
        self.assertEqual(self.serializers["state"].save.call_count, 1)

    def test_idempotent_producer_opt_in(self):
        idempotent = {
            **settings.LOGPIPE,
            "KAFKA_MAX_SEND_RETRIES": 5,
            "KAFKA_PRODUCER_KWARGS": {"acks": "all", "enable_idempotence": True},
        }
        with override_settings(LOGPIPE=idempotent):
            # Separate topic so the roundtrip test doesn't consume this record.
            producer = Producer("us-states-idempotent", StateSerializer_DRF)
            record = producer.send({"code": "PA", "name": "Pennsylvania"})
        self.assertEqual(record.topic, "us-states-idempotent")
        self.assertTrue(record.offset >= 0)
