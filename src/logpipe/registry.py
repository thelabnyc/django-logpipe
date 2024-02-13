from typing import Callable
import functools
from .consumer import Consumer

ConsumerFactory = Callable[[], Consumer]

_registered_consumers: list[ConsumerFactory] = []


def register_consumer(fn: ConsumerFactory) -> ConsumerFactory:
    _registered_consumers.append(fn)

    @functools.wraps(fn)
    def wrap() -> Consumer:
        return fn()

    return wrap


def list_registered_consumers() -> list[Consumer]:
    return [build() for build in _registered_consumers]


__all__ = ["register_consumer", "list_registered_consumers"]
