from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable, Mapping
from enum import Enum, auto
from typing import (
    IO,
    Any,
    ClassVar,
    Literal,
    NamedTuple,
    Protocol,
    TypeGuard,
    TypeVar,
)

from django.db import models
from pydantic import BaseModel
from rest_framework import serializers

MessageType = str
MessageVersion = int
TopicName = str

_IN = TypeVar("_IN", bound=models.Model)  # Instance Type


class Record(NamedTuple):
    topic: str
    partition: str
    offset: str | int
    timestamp: int | float
    key: str
    value: str | bytes


class RecordMetadata(NamedTuple):
    topic: str
    partition: str
    offset: str


class ConsumerBackend(Iterable[Record]):
    topic_name: TopicName

    def __init__(self, topic_name: TopicName, **kwargs: Any):
        pass

    def seek_to_sequence_number(
        self, shard: str, sequence_number: str | None = None
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self) -> ConsumerBackend:
        pass

    @abstractmethod
    def __next__(self) -> Record:
        pass


class ProducerBackend(Protocol):
    def send(
        self, topic_name: TopicName, key: str, value: bytes
    ) -> RecordMetadata | None:
        pass


class OffsetStoreBackend(Protocol):
    def commit(self, consumer: ConsumerBackend, message: Record) -> None:
        pass

    def seek(self, consumer: ConsumerBackend, topic: TopicName, partition: str) -> None:
        pass


class Renderer(Protocol):
    media_type: str
    format: str
    charset: str | None
    render_style: str

    def render(
        self,
        data: dict[str, Any],
        media_type: str | None = None,
        renderer_context: Mapping[str, Any] | None = None,
    ) -> bytes:
        pass


class Parser(Protocol):
    media_type: str

    def parse(
        self,
        stream: IO[Any],
        media_type: str | None = None,
        parser_context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        pass


class SerializerType(Enum):
    DRF = auto()
    PYDANTIC = auto()


class DRFSerializer(serializers.Serializer[_IN]):
    _tag: ClassVar[Literal[SerializerType.DRF]] = SerializerType.DRF
    MESSAGE_TYPE: ClassVar[str]
    VERSION: ClassVar[int]
    KEY_FIELD: ClassVar[str]

    @classmethod
    def lookup_instance(cls, **kwargs: Any) -> _IN | None:
        raise NotImplementedError()


class PydanticModel(BaseModel):
    _tag: ClassVar[Literal[SerializerType.PYDANTIC]] = SerializerType.PYDANTIC
    MESSAGE_TYPE: ClassVar[str]
    VERSION: ClassVar[int]
    KEY_FIELD: ClassVar[str]

    def save(self) -> Any:
        raise NotImplementedError()


SerializerClass = type[DRFSerializer[Any]] | type[PydanticModel]
Serializer = DRFSerializer[Any] | PydanticModel


def is_pydantic_serializer_class(
    cls: SerializerClass,
) -> TypeGuard[type[PydanticModel]]:
    return hasattr(cls, "_tag") and cls._tag == SerializerType.PYDANTIC
