# Generated by Django 1.11 on 2018-09-17 13:48

from django.db import migrations, models

import logpipe.settings


class Migration(migrations.Migration):
    dependencies = [
        ("logpipe", "0004_auto_20170502_1403"),
    ]

    operations = [
        migrations.AddField(
            model_name="kinesisoffset",
            name="region",
            field=models.CharField(
                choices=[
                    ("us-east-1", "US East (N. Virginia)"),
                    ("us-east-2", "US East (Ohio)"),
                    ("us-west-1", "US West (N. California)"),
                    ("us-west-2", "US West (Oregon)"),
                    ("ap-south-1", "Asia Pacific (Mumbai)"),
                    ("ap-northeast-2", "Asia Pacific (Seoul)"),
                    ("ap-southeast-1", "Asia Pacific (Singapore)"),
                    ("ap-southeast-2", "Asia Pacific (Sydney)"),
                    ("ap-northeast-1", "Asia Pacific (Tokyo)"),
                    ("ca-central-1", "Canada (Central)"),
                    ("eu-central-1", "EU (Frankfurt)"),
                    ("eu-west-1", "EU (Ireland)"),
                    ("eu-west-2", "EU (London)"),
                    ("eu-west-3", "EU (Paris)"),
                    ("sa-east-1", "South America (São Paulo)"),
                    ("cn-north-1", "China (Beijing)"),
                    ("us-gov-west-1", "AWS GovCloud (US)"),
                ],
                default=logpipe.settings.get_aws_region,
                help_text="The Kinesis stream region name",
                max_length=20,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="kinesisoffset",
            unique_together={("region", "stream", "shard")},
        ),
    ]
