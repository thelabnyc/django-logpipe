from django.test import TestCase, override_settings
from rest_framework.exceptions import ValidationError
from unittest.mock import MagicMock, patch
from logpipe import Producer
from .common import StateSerializer, StateModel, TOPIC_STATES


KAFKA = {
    'BOOTSTRAP_SERVERS': ['kafka:9092'],
    'RETRIES': 5,
    'TIMEOUT': 5,
}


class ProducerTest(TestCase):
    @override_settings(KAFKA=KAFKA)
    @patch('kafka.KafkaProducer')
    def test_normal_send(self, KafkaProducer):
        future = MagicMock()
        future.get.return_value = 'some-metadata'

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
        self.assertEqual(ret, 'some-metadata')
        self.assertEqual(KafkaProducer.call_count, 1)
        self.assertEqual(client.send.call_count, 1)
        self.assertEqual(future.get.call_count, 1)
        KafkaProducer.assert_called_with(bootstrap_servers=['kafka:9092'], retries=5)
        future.get.assert_called_with(timeout=5)


    @override_settings(KAFKA=KAFKA)
    @patch('kafka.KafkaProducer')
    def test_object_send(self, KafkaProducer):
        future = MagicMock()
        future.get.return_value = 'some-metadata'

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
        self.assertEqual(ret, 'some-metadata')
        self.assertEqual(KafkaProducer.call_count, 1)
        self.assertEqual(client.send.call_count, 1)
        self.assertEqual(future.get.call_count, 1)
        KafkaProducer.assert_called_with(bootstrap_servers=['kafka:9092'], retries=5)
        future.get.assert_called_with(timeout=5)


    @override_settings(KAFKA=KAFKA)
    @patch('kafka.KafkaProducer')
    def test_invalid_data(self, KafkaProducer):
        producer = Producer(TOPIC_STATES, StateSerializer)
        with self.assertRaises(ValidationError):
            producer.send({
                'code': 'NYC',
                'name': 'New York'
            })
        self.assertEqual(KafkaProducer.call_count, 0)
