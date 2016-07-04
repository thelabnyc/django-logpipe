from logpipe import Producer, Consumer
from .common import BaseTest, StateSerializer, TOPIC_STATES


class RoundTripTest(BaseTest):
    def test_roundtrip_state(self):
        def save(ser):
            self.assertEqual(ser.validated_data['code'], 'NY')
            self.assertEqual(ser.validated_data['name'], 'New York')
        FakeStateSerializer = self.mock_state_serializer(save)

        producer = Producer(TOPIC_STATES, StateSerializer)

        consumer = Consumer(TOPIC_STATES, consumer_timeout_ms=500)
        consumer.register(FakeStateSerializer)

        record = producer.send({'code': 'NY', 'name': 'New York'})
        self.assertEqual(record.topic, 'us-states')
        self.assertEqual(record.partition, 0)
        self.assertTrue(record.offset >= 0)

        consumer.run(iter_limit=1)

        self.assertEqual(FakeStateSerializer.call_count, 1)
        self.assertEqual(self.serializers['state'].save.call_count, 1)
