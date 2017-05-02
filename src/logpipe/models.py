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


class KinesisOffset(models.Model):
    stream = models.CharField(max_length=200,
        help_text='The Kinesis stream name')

    shard = models.CharField(max_length=20,
        help_text='The Kinesis shard ID')

    sequence_number = models.CharField(max_length=20,
        help_text='The current sequence number in the Kinesis shard')

    class Meta:
        unique_together = ('stream', 'shard')
        ordering = ('stream', 'shard', 'sequence_number')
