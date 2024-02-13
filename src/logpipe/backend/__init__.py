from __future__ import annotations

from typing import Any

from django.utils.module_loading import import_string

from .. import settings
from ..abc import ConsumerBackend, OffsetStoreBackend, ProducerBackend


def get_offset_backend() -> OffsetStoreBackend:
    default = "logpipe.backend.kafka.ModelOffsetStore"
    backend_path = settings.get("OFFSET_BACKEND", default)
    return import_string(backend_path)()


def get_consumer_backend(topic_name: str, **kwargs: Any) -> ConsumerBackend:
    default = "logpipe.backend.kafka.Consumer"
    backend_path = settings.get("CONSUMER_BACKEND", default)
    return import_string(backend_path)(topic_name, **kwargs)


def get_producer_backend() -> ProducerBackend:
    default = "logpipe.backend.kafka.Producer"
    backend_path = settings.get("PRODUCER_BACKEND", default)
    return import_string(backend_path)()
