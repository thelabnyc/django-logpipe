_registered_consumers = []


def register_consumer(fn):
    _registered_consumers.append(fn)

    def wrap():
        return fn()

    return wrap


def list_registered_consumers():
    return [build() for build in _registered_consumers]


__all__ = ["register_consumer", "list_registered_consumers"]
