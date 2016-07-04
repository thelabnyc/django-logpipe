from django.apps import AppConfig


class LPTesterConfig(AppConfig):
    name = 'lptester'

    def ready(self):
        from . import producers, consumers  # NOQA
