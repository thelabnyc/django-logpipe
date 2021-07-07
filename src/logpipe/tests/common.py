from django.test import TestCase
from rest_framework import serializers
from unittest.mock import MagicMock


TOPIC_STATES = "us-states"


class StateSerializer(serializers.Serializer):
    """Keyed Serializer for sending data about US States"""

    MESSAGE_TYPE = "us-state"
    VERSION = 1
    KEY_FIELD = "code"
    code = serializers.CharField(min_length=2, max_length=2)
    name = serializers.CharField()


class StateModel(object):
    code = ""
    name = ""


class BaseTest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializers = {}

    def mock_state_serializer(self, save=None):
        def make(*args, **kwargs):
            ser = StateSerializer(*args, **kwargs)
            ser.save = MagicMock()
            if save:
                ser.save.side_effect = lambda *args, **kwargs: save(
                    ser, *args, **kwargs
                )
            self.serializers["state"] = ser
            return ser

        FakeStateSerializer = MagicMock()
        FakeStateSerializer.MESSAGE_TYPE = StateSerializer.MESSAGE_TYPE
        FakeStateSerializer.VERSION = StateSerializer.VERSION
        FakeStateSerializer.side_effect = make

        return FakeStateSerializer
