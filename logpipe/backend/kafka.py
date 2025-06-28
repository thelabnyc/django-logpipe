from __future__ import annotations

from typing import Any, NotRequired, TypedDict
import logging

from django.apps import apps
import kafka

from .. import settings
from ..abc import (
    ConsumerBackend,
    OffsetStoreBackend,
    ProducerBackend,
    Record,
    RecordMetadata,
)
from ..exceptions import MissingTopicError
from . import get_offset_backend

logger = logging.getLogger(__name__)


class KafkaClientConfig(TypedDict):
    bootstrap_servers: list[str]
    retries: NotRequired[int]
    auto_offset_reset: NotRequired[str]
    enable_auto_commit: NotRequired[bool]
    consumer_timeout_ms: NotRequired[int]


class ModelOffsetStore(OffsetStoreBackend):
    def commit(self, consumer: ConsumerBackend, message: Record) -> None:
        if not isinstance(consumer, Consumer):
            raise TypeError("Consumer type mismatch")
        KafkaOffset = apps.get_model(app_label="logpipe", model_name="KafkaOffset")
        logger.debug(
            'Commit offset "%s" for topic "%s", partition "%s" to %s'
            % (
                message.offset,
                message.topic,
                message.partition,
                self.__class__.__name__,
            )
        )
        obj, created = KafkaOffset.objects.get_or_create(
            topic=message.topic, partition=message.partition
        )
        obj.offset = int(message.offset) + 1
        obj.save()

    def seek(self, consumer: ConsumerBackend, topic: str, partition: str) -> None:
        if not isinstance(consumer, Consumer):
            raise TypeError("Consumer type mismatch")
        KafkaOffset = apps.get_model(app_label="logpipe", model_name="KafkaOffset")
        tp = kafka.TopicPartition(topic=topic, partition=partition)
        try:
            obj = KafkaOffset.objects.get(topic=topic, partition=partition)
            logger.debug(
                'Seeking to offset "%s" on topic "%s", partition "%s"'
                % (obj.offset, topic, partition)
            )
            consumer.client.seek(tp, obj.offset)
        except KafkaOffset.DoesNotExist:
            logger.debug(
                'Seeking to beginning of topic "%s", partition "%s"'
                % (topic, partition)
            )
            consumer.client.seek_to_beginning(tp)


class KafkaOffsetStore(OffsetStoreBackend):
    def commit(self, consumer: ConsumerBackend, message: Record) -> None:
        if not isinstance(consumer, Consumer):
            raise TypeError("Consumer type mismatch")
        logger.debug(
            'Commit offset "%s" for topic "%s", partition "%s" to %s'
            % (
                message.offset,
                message.topic,
                message.partition,
                self.__class__.__name__,
            )
        )
        consumer.client.commit()

    def seek(self, consumer: ConsumerBackend, topic: str, partition: str) -> None:
        pass


class Consumer(ConsumerBackend):
    _client = None

    def __init__(self, topic_name: str, **kwargs: Any):
        self.topic_name = topic_name
        self.client_kwargs = kwargs

    @property
    def client(self) -> kafka.KafkaConsumer:
        if not self._client:
            kwargs = self._get_client_config()
            self._client = kafka.KafkaConsumer(**kwargs)
            tps = self._get_topic_partitions()
            self._client.assign(tps)
            backend = get_offset_backend()
            for tp in tps:
                backend.seek(self, tp.topic, tp.partition)
                self._client.committed(tp)
        return self._client

    def __iter__(self) -> Consumer:
        return self

    def __next__(self) -> Record:
        r = next(self.client)
        record = Record(
            topic=r.topic,
            partition=r.partition,
            offset=r.offset,
            timestamp=r.timestamp,
            key=r.key,
            value=r.value,
        )
        return record

    def _get_topic_partitions(self) -> list[kafka.TopicPartition]:
        p = []
        partitions = self.client.partitions_for_topic(self.topic_name)
        if not partitions:
            raise MissingTopicError(
                "Could not find topic %s. Does it exist?" % self.topic_name
            )
        for partition in partitions:
            tp = kafka.TopicPartition(self.topic_name, partition=partition)
            p.append(tp)
        return p

    def _get_client_config(self) -> KafkaClientConfig:
        kwargs = KafkaClientConfig(
            bootstrap_servers=settings.get("KAFKA_BOOTSTRAP_SERVERS"),
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            consumer_timeout_ms=1000,
        )
        kwargs.update(settings.get("KAFKA_KWARGS", {}))
        kwargs.update(settings.get("KAFKA_CONSUMER_KWARGS", {}))
        kwargs.update(self.client_kwargs)  # type: ignore[typeddict-item]
        return kwargs


class Producer(ProducerBackend):
    _client = None

    @property
    def client(self) -> kafka.KafkaProducer:
        if not self._client:
            kwargs = self._get_client_config()
            self._client = kafka.KafkaProducer(**kwargs)
        return self._client

    def send(self, topic_name: str, key: str, value: bytes) -> RecordMetadata:
        keybytes = key.encode()
        timeout = settings.get("KAFKA_SEND_TIMEOUT", 10)
        future = self.client.send(topic_name, key=keybytes, value=value)
        metadata = future.get(timeout=timeout)
        return RecordMetadata(
            topic=topic_name,
            partition=metadata.partition,
            offset=metadata.offset,
        )

    def _get_client_config(self) -> KafkaClientConfig:
        servers = settings.get("KAFKA_BOOTSTRAP_SERVERS")
        retries = settings.get("KAFKA_MAX_SEND_RETRIES", 0)
        kwargs = KafkaClientConfig(
            bootstrap_servers=servers,
            retries=retries,
        )
        kwargs.update(settings.get("KAFKA_KWARGS", {}))
        return kwargs
