from django.test import TestCase, override_settings
from kafka.consumer.fetcher import ConsumerRecord
from rest_framework.exceptions import ValidationError
from unittest.mock import MagicMock, patch
from logpipe import Producer
from logpipe.tests.common import StateSerializer, StateModel, TOPIC_STATES
import binascii


LOGPIPE = {
    'KAFKA_BOOTSTRAP_SERVERS': ['kafka:9092'],
    'KAFKA_SEND_TIMEOUT': 5,
    'KAFKA_MAX_SEND_RETRIES': 5,
}


class ProducerTest(TestCase):
    @override_settings(LOGPIPE=LOGPIPE)
    @patch('kafka.KafkaProducer')
    def test_normal_send(self, KafkaProducer):
        future = MagicMock()
        future.get.return_value = self._get_record_metadata()

        def test_send_call(topic, key, value):
            self.assertEqual(topic, 'us-states')
            self.assertEqual(key, b'NY')
            self.assertIn(b'json:', value)
            self.assertIn(b'"message":{"', value)
            self.assertIn(b'"code":"NY"', value)
            self.assertIn(b'"name":"New York"', value)
            self.assertIn(b'"version":1', value)
            return future

        client = MagicMock()
        client.send.side_effect = test_send_call
        KafkaProducer.return_value = client

        producer = Producer(TOPIC_STATES, StateSerializer)
        ret = producer.send({
            'code': 'NY',
            'name': 'New York'
        })
        self.assertEqual(ret.topic, TOPIC_STATES)
        self.assertEqual(ret.partition, 0)
        self.assertEqual(ret.offset, 42)
        self.assertEqual(KafkaProducer.call_count, 1)
        self.assertEqual(client.send.call_count, 1)
        self.assertEqual(future.get.call_count, 1)
        KafkaProducer.assert_called_with(bootstrap_servers=['kafka:9092'], retries=5)
        future.get.assert_called_with(timeout=5)


    @override_settings(LOGPIPE=LOGPIPE)
    @patch('kafka.KafkaProducer')
    def test_object_send(self, KafkaProducer):
        future = MagicMock()
        future.get.return_value = self._get_record_metadata()

        def test_send_call(topic, key, value):
            self.assertEqual(topic, 'us-states')
            self.assertEqual(key, b'NY')
            self.assertIn(b'json:', value)
            self.assertIn(b'"message":{"', value)
            self.assertIn(b'"code":"NY"', value)
            self.assertIn(b'"name":"New York"', value)
            self.assertIn(b'"version":1', value)
            return future

        client = MagicMock()
        client.send.side_effect = test_send_call
        KafkaProducer.return_value = client

        producer = Producer(TOPIC_STATES, StateSerializer)
        obj = StateModel()
        obj.code = 'NY'
        obj.name = 'New York'
        ret = producer.send(obj)
        self.assertEqual(ret.topic, TOPIC_STATES)
        self.assertEqual(ret.partition, 0)
        self.assertEqual(ret.offset, 42)
        self.assertEqual(KafkaProducer.call_count, 1)
        self.assertEqual(client.send.call_count, 1)
        self.assertEqual(future.get.call_count, 1)
        KafkaProducer.assert_called_with(bootstrap_servers=['kafka:9092'], retries=5)
        future.get.assert_called_with(timeout=5)


    @override_settings(LOGPIPE=LOGPIPE)
    @patch('kafka.KafkaProducer')
    def test_invalid_data(self, KafkaProducer):
        producer = Producer(TOPIC_STATES, StateSerializer)
        with self.assertRaises(ValidationError):
            producer.send({
                'code': 'NYC',
                'name': 'New York'
            })
        self.assertEqual(KafkaProducer.call_count, 0)


    def _get_record_metadata(self):
        return ConsumerRecord(
            topic=TOPIC_STATES,
            partition=0,
            offset=42,
            timestamp=1467649216540,
            timestamp_type=0,
            key=b'NY',
            value=b'foo',
            checksum=binascii.crc32(b'foo'),
            serialized_key_size=b'NY',
            serialized_value_size=b'foo')
