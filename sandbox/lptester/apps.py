from django.apps import AppConfig


class LPTesterConfig(AppConfig):
    name = "sandbox.lptester"
    label = "lptester"
    default = True

    def ready(self):
        from . import producers, consumers  # NOQA
