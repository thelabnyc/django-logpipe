# Generated by Django 1.11 on 2017-05-02 14:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logpipe", "0003_auto_20170427_1703"),
    ]

    operations = [
        migrations.AlterField(
            model_name="kinesisoffset",
            name="sequence_number",
            field=models.CharField(
                help_text="The current sequence number in the Kinesis shard",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="kinesisoffset",
            name="shard",
            field=models.CharField(help_text="The Kinesis shard ID", max_length=200),
        ),
    ]
