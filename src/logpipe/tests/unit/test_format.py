import pickle

from django.test import TestCase, override_settings

from logpipe.constants import FORMAT_PICKLE
from logpipe.exceptions import UnknownFormatError
from logpipe.formats.pickle import PickleParser, PickleRenderer
import logpipe.format


class JSONFormatTest(TestCase):
    def test_render(self):
        msg = logpipe.format.render(
            "json",
            {
                "foo": "bar",
            },
        )
        self.assertEqual(msg, b'json:{"foo":"bar"}')

    def test_parse(self):
        data = logpipe.format.parse(b'json:{"foo":"bar"}')
        self.assertEqual(
            data,
            {
                "foo": "bar",
            },
        )


class MsgPackFormatTest(TestCase):
    def test_render(self):
        msg = logpipe.format.render("msgpack", {"foo": "bar"})
        self.assertEqual(msg, b"msgpack:\x81\xa3foo\xa3bar")

    def test_parse(self):
        data = logpipe.format.parse(b"msgpack:\x81\xa3foo\xa3bar")
        self.assertEqual(
            data,
            {
                "foo": "bar",
            },
        )


class PickleFormatTest(TestCase):
    @override_settings(LOGPIPE={"BOOTSTRAP_SERVERS": ["kafka:9092"]})
    def test_default(self):
        with self.assertRaises(UnknownFormatError):
            logpipe.format.render("pickle", {})

    def test_render(self):
        logpipe.format.register(FORMAT_PICKLE, PickleRenderer(), PickleParser())
        msg = logpipe.format.render("pickle", {"foo": "bar"})
        self.assertTrue(msg.startswith(b"pickle:"))
        self.assertEqual(pickle.loads(msg.replace(b"pickle:", b"")), {"foo": "bar"})
        logpipe.format.unregister(FORMAT_PICKLE)

    def test_parse(self):
        logpipe.format.register(FORMAT_PICKLE, PickleRenderer(), PickleParser())
        data = logpipe.format.parse(
            b"pickle:\x80\x03}q\x00X\x03\x00\x00\x00fooq\x01X\x03\x00\x00\x00barq\x02s."
        )
        self.assertEqual(
            data,
            {
                "foo": "bar",
            },
        )
        logpipe.format.unregister(FORMAT_PICKLE)


class UnknownFormatTest(TestCase):
    def test_render(self):
        with self.assertRaises(UnknownFormatError):
            logpipe.format.render("xml", {})

    def test_parse(self):
        with self.assertRaises(UnknownFormatError):
            logpipe.format.parse(b"xml:<foo>bar</foo>")
