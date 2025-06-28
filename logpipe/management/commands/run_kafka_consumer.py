from typing import Any

from django.core.management.base import BaseCommand

from logpipe.consumer import MultiConsumer
from logpipe.registry import list_registered_consumers


class Command(BaseCommand):
    help = "Fetch and apply Kafka messages"

    def handle(self, *args: Any, **options: Any) -> None:
        consumers = list_registered_consumers()
        for c in consumers:
            print("Found consumer: %s" % c)
        print("Running indefinite consumer...")
        multi = MultiConsumer(*consumers)
        multi.run()
