# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-27 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logpipe", "0001_initial"),
    ]

    operations = [migrations.RenameModel("Offset", "KafkaOffset")]
