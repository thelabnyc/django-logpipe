from __future__ import annotations

from typing import Any
import collections
import time

from ..abc import (
    ConsumerBackend,
    OffsetStoreBackend,
    ProducerBackend,
    Record,
    RecordMetadata,
    TopicName,
)

_topics: dict[TopicName, collections.deque[Record]] = {}
_offsets: collections.Counter[str] = collections.Counter()


def reset_topics() -> None:
    global _topics, _offsets
    _topics = {}
    _offsets = collections.Counter()
    return None


class Consumer(ConsumerBackend):
    def __init__(self, topic_name: str, **kwargs: Any):
        self.topic_name = topic_name

    def seek_to_sequence_number(
        self, shard: str, sequence_number: str | None = None
    ) -> None:
        pass

    def __iter__(self) -> Consumer:
        return self

    def __next__(self) -> Record:
        _records = _topics.get(self.topic_name)
        if _records:
            try:
                return _records.popleft()
            except IndexError:
                pass
        raise StopIteration()


class Producer(ProducerBackend):
    def send(
        self, topic_name: TopicName, key: str, value: bytes
    ) -> RecordMetadata | None:
        _offsets[topic_name] += 1
        record = Record(
            topic=topic_name,
            partition="0",
            offset=_offsets[topic_name],
            timestamp=(time.time() * 1000),
            key=key,
            value=value,
        )
        if topic_name not in _topics:
            _topics[topic_name] = collections.deque()
        _topics[topic_name].append(record)
        return RecordMetadata(
            topic=topic_name,
            partition=record.partition,
            offset=str(record.offset),
        )


class ModelOffsetStore(OffsetStoreBackend):
    def commit(self, consumer: ConsumerBackend, message: Record) -> None:
        pass

    def seek(self, consumer: ConsumerBackend, topic: TopicName, partition: str) -> None:
        pass
