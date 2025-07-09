from dataclasses import dataclass
from typing import ClassVar
from unittest.mock import MagicMock

from django.test import TestCase
from pydantic import Field
from rest_framework import serializers

from ..abc import PydanticModel

TOPIC_STATES = "us-states"


class StateSerializer_DRF(serializers.Serializer):
    """Keyed Serializer for sending data about US States"""

    MESSAGE_TYPE = "us-state"
    VERSION = 1
    KEY_FIELD = "code"
    code = serializers.CharField(min_length=2, max_length=2)
    name = serializers.CharField()


class State_Pydantic(PydanticModel):
    MESSAGE_TYPE: ClassVar[str] = "us-state"
    VERSION: ClassVar[int] = 1
    KEY_FIELD: ClassVar[str] = "code"

    code: str = Field(
        ...,
        max_length=2,
        min_length=2,
    )
    name: str = ""


@dataclass
class StateModel:
    id: int | None = None
    code: str = ""
    name: str = ""


class BaseTest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializers = {}

    def mock_state_serializer_drf(self, save=None):
        def make(*args, **kwargs):
            ser = StateSerializer_DRF(*args, **kwargs)
            ser.save = MagicMock()
            if save:
                ser.save.side_effect = lambda *args, **kwargs: save(ser, *args, **kwargs)
            self.serializers["state"] = ser
            return ser

        FakeStateSerializer = MagicMock()
        FakeStateSerializer.MESSAGE_TYPE = StateSerializer_DRF.MESSAGE_TYPE
        FakeStateSerializer.VERSION = StateSerializer_DRF.VERSION
        FakeStateSerializer.side_effect = make

        return FakeStateSerializer

    def mock_state_serializer_pydantic(self, save=None):
        class MockState_Pydantic(State_Pydantic):
            def save(self):
                if save:
                    save(self)

        return MockState_Pydantic
