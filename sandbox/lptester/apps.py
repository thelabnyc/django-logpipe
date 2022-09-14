from django.apps import AppConfig


class LPTesterConfig(AppConfig):
    name = "lptester"
    default = True

    def ready(self):
        from . import producers, consumers  # NOQA
