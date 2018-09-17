from django.db import models
from . import settings


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


    def __str__(self):
        return 'topic="{}", partition="{}", offset="{}"'.format(self.topic, self.partition, self.offset)


class KinesisOffset(models.Model):
    region = models.CharField(max_length=20,
        help_text='The Kinesis stream region name',
        default=settings.get_aws_region,
        choices=(
            ('us-east-1', "US East (N. Virginia)"),
            ('us-east-2', "US East (Ohio)"),
            ('us-west-1', "US West (N. California)"),
            ('us-west-2', "US West (Oregon)"),
            ('ap-south-1', "Asia Pacific (Mumbai)"),
            ('ap-northeast-2', "Asia Pacific (Seoul)"),
            ('ap-southeast-1', "Asia Pacific (Singapore)"),
            ('ap-southeast-2', "Asia Pacific (Sydney)"),
            ('ap-northeast-1', "Asia Pacific (Tokyo)"),
            ('ca-central-1', "Canada (Central)"),
            ('eu-central-1', "EU (Frankfurt)"),
            ('eu-west-1', "EU (Ireland)"),
            ('eu-west-2', "EU (London)"),
            ('eu-west-3', "EU (Paris)"),
            ('sa-east-1', "South America (São Paulo)"),
            ('cn-north-1', "China (Beijing)"),
            ('us-gov-west-1', "AWS GovCloud (US)"),
        ))

    stream = models.CharField(max_length=200,
        help_text='The Kinesis stream name')

    shard = models.CharField(max_length=200,
        help_text='The Kinesis shard ID')

    sequence_number = models.CharField(max_length=200,
        help_text='The current sequence number in the Kinesis shard')

    class Meta:
        unique_together = ('region', 'stream', 'shard')
        ordering = ('stream', 'shard', 'sequence_number')

    def __str__(self):
        return 'region="{}", stream="{}", shard="{}", sequence_number="{}"'.format(self.region, self.stream, self.shard, self.sequence_number)
