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

        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=1000)
        consumer.register(FakeStateSerializer)
        consumer.run(iter_limit=1)

        self.assertEqual(FakeStateSerializer.call_count, 1)
        self.assertEqual(self.serializers["state"].save.call_count, 1)
