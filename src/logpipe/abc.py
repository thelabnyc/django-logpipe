from __future__ import annotations
from abc import abstractmethod
from collections.abc import Mapping
from django.db import models
from typing import (
    Protocol,
    Any,
    IO,
    NamedTuple,
    Iterable,
)
from rest_framework import serializers

MessageType = str
MessageVersion = int
TopicName = str


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
        ...

    def seek_to_sequence_number(
        self, shard: str, sequence_number: str | None = None
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self) -> ConsumerBackend:
        ...

    @abstractmethod
    def __next__(self) -> Record:
        ...


class ProducerBackend(Protocol):
    def send(
        self, topic_name: TopicName, key: str, value: bytes
    ) -> RecordMetadata | None:
        ...


class OffsetStoreBackend(Protocol):
    def commit(self, consumer: ConsumerBackend, message: Record) -> None:
        ...

    def seek(self, consumer: ConsumerBackend, topic: TopicName, partition: str) -> None:
        ...


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
        ...


class Parser(Protocol):
    media_type: str

    def parse(
        self,
        stream: IO[Any],
        media_type: str | None = None,
        parser_context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...


class DRFSerializer(serializers.Serializer[Any]):
    MESSAGE_TYPE: str
    VERSION: int
    KEY_FIELD: str

    @classmethod
    def lookup_instance(cls, **kwargs: dict[str, Any]) -> models.Model | None:
        pass
