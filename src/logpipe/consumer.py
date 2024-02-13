from typing import Any, Generator, Iterator
from django.db import transaction
from rest_framework import serializers
from .exceptions import (
    InvalidMessageError,
    ValidationError,
    IgnoredMessageTypeError,
    UnknownMessageTypeError,
    UnknownMessageVersionError,
)
from .backend import get_offset_backend, get_consumer_backend
from .format import parse
from .abc import Record, DRFSerializer, ConsumerBackend, MessageType, MessageVersion
from . import settings
import itertools
import logging
import time


logger = logging.getLogger(__name__)


def consumer_error_handler(
    inner: "Consumer",
) -> Generator[tuple[Record, DRFSerializer], None, None]:
    while True:
        # Try to get the next message
        try:
            yield next(inner)

        # Obey the laws of StopIteration
        except StopIteration:
            return

        # Message format was invalid in some way: log error and move on.
        except InvalidMessageError as e:
            logger.error(
                "Failed to deserialize message in topic {}. Details: {}".format(
                    inner.consumer.topic_name, e
                )
            )
            inner.commit(e.message)

        # Message type has been explicitly ignored: skip it silently and move on.
        except IgnoredMessageTypeError as e:
            logger.debug(
                "Skipping ignored message type in topic {}. Details: {}".format(
                    inner.consumer.topic_name, e
                )
            )
            inner.commit(e.message)

        # Message type is unknown: log error and move on.
        except UnknownMessageTypeError as e:
            logger.error(
                "Skipping unknown message type in topic {}. Details: {}".format(
                    inner.consumer.topic_name, e
                )
            )
            inner.commit(e.message)

        # Message version is unknown: log error and move on.
        except UnknownMessageVersionError as e:
            logger.error(
                "Skipping unknown message version in topic {}. Details: {}".format(
                    inner.consumer.topic_name, e
                )
            )
            inner.commit(e.message)

        # Serializer for message type flagged message as invalid: log warning and move on.
        except ValidationError as e:
            logger.warning(
                "Skipping invalid message in topic {}. Details: {}".format(
                    inner.consumer.topic_name, e
                )
            )
            inner.commit(e.message)

        pass


class Consumer(Iterator[tuple[Record, DRFSerializer]]):
    _client = None
    consumer: ConsumerBackend
    throw_errors: bool
    serializer_classes: dict[MessageType, dict[MessageVersion, type[DRFSerializer]]]
    ignored_message_types: set[MessageType]

    def __init__(self, topic_name: str, throw_errors: bool = False, **kwargs: Any):
        self.consumer = get_consumer_backend(topic_name, **kwargs)
        self.throw_errors = throw_errors
        self.serializer_classes = {}
        self.ignored_message_types = set([])

    def add_ignored_message_type(self, message_type: MessageType) -> None:
        self.ignored_message_types.add(message_type)

    def commit(self, message: Record) -> None:
        get_offset_backend().commit(self.consumer, message)

    def register(self, serializer_class: type[DRFSerializer]) -> None:
        message_type = serializer_class.MESSAGE_TYPE
        version = serializer_class.VERSION
        if message_type not in self.serializer_classes:
            self.serializer_classes[message_type] = {}
        self.serializer_classes[message_type][version] = serializer_class

    def run(self, iter_limit: int = 0) -> None:
        i = 0
        for message, serializer in self:
            with transaction.atomic():
                try:
                    serializer.save()
                    self.commit(message)
                except Exception as e:
                    info = (
                        message.key,
                        message.topic,
                        message.partition,
                        message.offset,
                    )
                    logger.exception(
                        'Failed to process message with key "%s" from topic "%s", partition "%s", offset "%s"'
                        % info
                    )
                    raise e
            i += 1
            if iter_limit > 0 and i >= iter_limit:
                break

    def __iter__(self) -> Iterator[tuple[Record, DRFSerializer]]:
        if self.throw_errors:
            return self
        return consumer_error_handler(self)

    def __next__(self) -> tuple[Record, DRFSerializer]:
        return self._get_next_message()

    def __str__(self) -> str:
        return '<logpipe.consumer.Consumer topic="%s">' % self.consumer.topic_name

    def _get_next_message(self) -> tuple[Record, DRFSerializer]:
        message = next(self.consumer)

        info = (message.key, message.topic, message.partition, message.offset)
        logger.debug(
            'Received message with key "%s" from topic "%s", partition "%s", offset "%s"'
            % info
        )

        # Wait?
        timestamp = getattr(message, "timestamp", None) or (time.time() * 1000)
        lag_ms = (time.time() * 1000) - timestamp
        logger.debug("Message lag is %sms" % lag_ms)
        wait_ms = settings.get("MIN_MESSAGE_LAG_MS", 0) - lag_ms
        if wait_ms > 0:
            logger.debug("Respecting MIN_MESSAGE_LAG_MS by waiting %sms" % wait_ms)
            time.sleep(wait_ms / 1000)
            logger.debug("Finished waiting")

        try:
            serializer = self._unserialize(message)
        except Exception as e:
            raise e

        return message, serializer

    def _unserialize(self, message: Record) -> DRFSerializer:
        data = parse(message.value)
        if "type" not in data:
            raise InvalidMessageError(
                'Received message missing missing a top-level "type" key.', message
            )
        if "version" not in data:
            raise InvalidMessageError(
                'Received message missing missing a top-level "version" key.', message
            )
        if "message" not in data:
            raise InvalidMessageError(
                'Received message missing missing a top-level "message" key.', message
            )

        message_type = data["type"]
        if message_type in self.ignored_message_types:
            raise IgnoredMessageTypeError(
                'Received message with ignored type "%s" in topic %s'
                % (message_type, message.topic),
                message,
            )
        if message_type not in self.serializer_classes:
            raise UnknownMessageTypeError(
                'Received message with unknown type "%s" in topic %s'
                % (message_type, message.topic),
                message,
            )

        version = data["version"]
        if version not in self.serializer_classes[message_type]:
            raise UnknownMessageVersionError(
                'Received message of type "%s" with unknown version "%s" in topic %s'
                % (message_type, version, message.topic),
                message,
            )

        serializer_class = self.serializer_classes[message_type][version]

        instance = None
        if hasattr(serializer_class, "lookup_instance"):
            instance = serializer_class.lookup_instance(**data["message"])
        serializer = serializer_class(instance=instance, data=data["message"])

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            raise ValidationError(e, message)

        return serializer


class MultiConsumer:
    consumers: list[Consumer]

    def __init__(self, *consumers: Consumer):
        self.consumers = list(consumers)

    def run(self) -> None:
        for consumer in itertools.cycle(self.consumers):
            consumer.run(iter_limit=1)
