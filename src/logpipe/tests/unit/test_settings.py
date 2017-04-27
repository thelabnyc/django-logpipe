from django.test import TestCase, override_settings
from django.core.exceptions import ImproperlyConfigured
from logpipe import settings


class ProducerTest(TestCase):
    @override_settings(LOGPIPE={'BOOTSTRAP_SERVERS': ['kafka:9092']})
    def test_normal_required_key(self):
        self.assertEqual(settings.get('BOOTSTRAP_SERVERS'), ['kafka:9092'])


    @override_settings(LOGPIPE={'BOOTSTRAP_SERVERS': ['kafka:9092'], 'RETRIES': 3})
    def test_normal_optional_key(self):
        self.assertEqual(settings.get('RETRIES', 5), 3)


    @override_settings(LOGPIPE={})
    def test_missing_required_key(self):
        with self.assertRaises(ImproperlyConfigured):
            settings.get('BOOTSTRAP_SERVERS')


    @override_settings(LOGPIPE={'BOOTSTRAP_SERVERS': ['kafka:9092']})
    def test_missing_optional_key(self):
        self.assertEqual(settings.get('RETRIES', 5), 5)
