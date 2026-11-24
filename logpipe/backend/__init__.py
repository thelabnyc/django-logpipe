from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any
import logging

from django.utils.module_loading import import_string

from .. import settings
from ..abc import ConsumerBackend, OffsetStoreBackend, ProducerBackend

logger = logging.getLogger(__name__)


class ProducerScope:
    def __init__(self) -> None:
        self.backends: dict[str, ProducerBackend] = {}
        self.closed: bool = False


_scoped_producers: ContextVar[ProducerScope | None] = ContextVar(
    "_scoped_producers",
    default=None,
)


def get_active_producer_scope() -> ProducerScope | None:
    """Return the currently active `reuse_producer()` scope, or None if no open scope is active."""
    scope = _scoped_producers.get()
    if scope is None or scope.closed:
        return None
    return scope


@contextmanager
def reuse_producer() -> Iterator[None]:
    """Reuse ProducerBackend instances across Producer constructions within this block and close them on exit."""
    if get_active_producer_scope() is not None:
        yield
        return
    scope = ProducerScope()
    token = _scoped_producers.set(scope)
    try:
        yield
    finally:
        scope.closed = True
        backends = list(scope.backends.values())
        scope.backends.clear()
        _scoped_producers.reset(token)
        for backend in backends:
            close = getattr(backend, "close", None)
            if callable(close):
                try:
                    close()
                except Exception:
                    logger.exception("Failed to close scoped producer backend %r", backend)


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
    scope = get_active_producer_scope()
    if scope is not None:
        if backend_path not in scope.backends:
            scope.backends[backend_path] = import_string(backend_path)()
        return scope.backends[backend_path]
    return import_string(backend_path)()
