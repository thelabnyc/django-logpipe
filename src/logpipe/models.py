from django.db import models
from django.utils.translation import gettext_lazy as _
from . import settings


class KafkaOffset(models.Model):
    # Translators: Internal Model Field Name
    topic = models.CharField(_('Kafka Topic Name'),
        # Translators: Interal Model Field Help Text
        help_text=_('The Kafka topic name'),
        max_length=200)

    # Translators: Internal Model Field Name
    partition = models.PositiveIntegerField(_('Kafka Partition ID'),
        # Translators: Interal Model Field Help Text
        help_text=_('The Kafka partition identifier'))

    # Translators: Internal Model Field Name
    offset = models.PositiveIntegerField(_('Kafka Offset'),
        # Translators: Interal Model Field Help Text
        help_text=_('The current offset in the Kafka partition'),
        default=0)

    class Meta:
        # Translators: Internal Model Name (singular)
        verbose_name = _('Kafka Offset')
        # Translators: Internal Model Name (plural)
        verbose_name_plural = _('Kafka Offsets')
        unique_together = ('topic', 'partition')
        ordering = ('topic', 'partition', 'offset')


    def __str__(self):
        return 'topic="{}", partition="{}", offset="{}"'.format(self.topic, self.partition, self.offset)


class KinesisOffset(models.Model):
    _region_choices = (
        # Translators: AWS Region Name
        ('us-east-1', _("US East (N. Virginia)")),
        # Translators: AWS Region Name
        ('us-east-2', _("US East (Ohio)")),
        # Translators: AWS Region Name
        ('us-west-1', _("US West (N. California)")),
        # Translators: AWS Region Name
        ('us-west-2', _("US West (Oregon)")),
        # Translators: AWS Region Name
        ('ap-south-1', _("Asia Pacific (Mumbai)")),
        # Translators: AWS Region Name
        ('ap-northeast-2', _("Asia Pacific (Seoul)")),
        # Translators: AWS Region Name
        ('ap-southeast-1', _("Asia Pacific (Singapore)")),
        # Translators: AWS Region Name
        ('ap-southeast-2', _("Asia Pacific (Sydney)")),
        # Translators: AWS Region Name
        ('ap-northeast-1', _("Asia Pacific (Tokyo)")),
        # Translators: AWS Region Name
        ('ca-central-1', _("Canada (Central)")),
        # Translators: AWS Region Name
        ('eu-central-1', _("EU (Frankfurt)")),
        # Translators: AWS Region Name
        ('eu-west-1', _("EU (Ireland)")),
        # Translators: AWS Region Name
        ('eu-west-2', _("EU (London)")),
        # Translators: AWS Region Name
        ('eu-west-3', _("EU (Paris)")),
        # Translators: AWS Region Name
        ('sa-east-1', _("South America (São Paulo)")),
        # Translators: AWS Region Name
        ('cn-north-1', _("China (Beijing)")),
        # Translators: AWS Region Name
        ('us-gov-west-1', _("AWS GovCloud (US)")),
    )

    # Translators: Internal Model Field Name
    region = models.CharField(_('AWS Region'),
        # Translators: Interal Model Field Help Text
        help_text=_('The Kinesis stream region name'),
        max_length=20,
        default=settings.get_aws_region,
        choices=_region_choices)

    # Translators: Internal Model Field Name
    stream = models.CharField(_('Kinesis Stream Name'),
        # Translators: Interal Model Field Help Text
        help_text=_('The Kinesis stream name'),
        max_length=200)

    # Translators: Internal Model Field Name
    shard = models.CharField(_('Kinesis Shard ID'),
        # Translators: Interal Model Field Help Text
        help_text=_('The Kinesis shard ID'),
        max_length=200)

    # Translators: Internal Model Field Name
    sequence_number = models.CharField(_('Kinesis Sequence Number'),
        # Translators: Interal Model Field Help Text
        help_text=_('The current sequence number in the Kinesis shard'),
        max_length=200)

    class Meta:
        # Translators: Internal Model Name (singular)
        verbose_name = _('AWS Kinesis Offset')
        # Translators: Internal Model Name (plural)
        verbose_name_plural = _('AWS Kinesis Offsets')
        unique_together = ('region', 'stream', 'shard')
        ordering = ('stream', 'shard', 'sequence_number')

    def __str__(self):
        return 'region="{}", stream="{}", shard="{}", sequence_number="{}"'.format(self.region, self.stream, self.shard, self.sequence_number)
