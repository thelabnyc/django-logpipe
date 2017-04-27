from django.db import models


class KafkaOffset(models.Model):
    topic = models.CharField(max_length=200,
        help_text='The Kafka topic name')

    partition = models.PositiveIntegerField(
        help_text='The Kafka partition identifier')

    offset = models.PositiveIntegerField(default=0,
        help_text='The current offset in the Kafka partition')

    class Meta:
        unique_together = ('topic', 'partition')
        ordering = ('topic', 'partition', 'offset')
