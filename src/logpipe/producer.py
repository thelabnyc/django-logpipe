from typing import Any
import logging

from django.db import models

from . import settings
from .abc import DRFSerializer, ProducerBackend, PydanticModel, RecordMetadata
from .backend import get_producer_backend
from .constants import FORMAT_JSON
from .format import render

logger = logging.getLogger(__name__)


class BaseProducer:
    client: ProducerBackend
    topic_name: str
    producer_id: str

    def __init__(
        self,
        topic_name: str,
        producer_id: str | None = None,
    ):
        self.client = get_producer_backend()
        self.topic_name = topic_name
        self.producer_id = (
            producer_id if producer_id else settings.get("PRODUCER_ID", "")
        )

    def _inner_send(
        self,
        message_type: str,
        version: int,
        key: str,
        data: Any,
    ) -> RecordMetadata | None:
        # Render everything into a string
        renderer = settings.get("DEFAULT_FORMAT", FORMAT_JSON)
        body = {
            "type": message_type,
            "version": version,
            "message": data,
        }
        if self.producer_id:
            body["producer"] = self.producer_id
        serialized_data = render(renderer, body)

        # Send the message data into the backend
        record_metadata = self.client.send(
            self.topic_name,
            key=key,
            value=serialized_data,
        )
        logger.debug(
            'Sent message with type "%s", key "%s" to topic "%s"'
            % (message_type, key, self.topic_name)
        )
        return record_metadata


class DRFProducer(BaseProducer):
    """
    Producer class for sending messages that are serialized using a Django Rest
    Framework serializer.
    """

    serializer_class: type[DRFSerializer]

    def __init__(
        self,
        topic_name: str,
        serializer_class: type[DRFSerializer],
        producer_id: str | None = None,
    ):
        super().__init__(topic_name, producer_id)
        self.serializer_class = serializer_class

    def send(self, instance: dict[str, Any] | models.Model) -> RecordMetadata | None:
        """
        Serialize the given object using the previously specified serializer, then
        write it to the log backend (Kafka or Kinesis).
        """
        # Get the message type and version
        message_type = self.serializer_class.MESSAGE_TYPE
        version = self.serializer_class.VERSION

        # Init the serializer
        ser = self.serializer_class(instance=instance)

        # Get the message's partition key
        key_field = getattr(self.serializer_class, "KEY_FIELD", None)
        key = ""
        if key_field:
            key = str(ser.data[key_field])

        # Send
        return self._inner_send(
            message_type=message_type,
            version=version,
            key=key,
            data=ser.data,
        )


# For backwards compatibility
Producer = DRFProducer


class PydanticProducer(BaseProducer):
    def send(self, instance: PydanticModel) -> RecordMetadata | None:
        # Get the message's partition key
        key_field = getattr(instance, "KEY_FIELD", None)
        key = ""
        if key_field:
            key = str(getattr(instance, key_field))

        # Send
        return self._inner_send(
            message_type=instance.MESSAGE_TYPE,
            version=instance.VERSION,
            key=key,
            data=instance.model_dump(mode="json"),
        )
