from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LogpipeConfig(AppConfig):
    name = "logpipe"
    label = "logpipe"
    # Translators: Backend Library Name
    verbose_name = _("LogPipe")
