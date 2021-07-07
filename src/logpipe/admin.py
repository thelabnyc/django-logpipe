from django.contrib import admin
from . import models


@admin.register(models.KafkaOffset)
class KafkaOffsetAdmin(admin.ModelAdmin):
    fields = ["topic", "partition", "offset"]
    list_display = ["topic", "partition", "offset"]
    list_filter = ["topic", "partition"]
    readonly_fields = ["topic", "partition"]


@admin.register(models.KinesisOffset)
class KinesisOffsetAdmin(admin.ModelAdmin):
    fields = ["region", "stream", "shard", "sequence_number"]
    list_display = ["stream", "region", "shard", "sequence_number"]
    list_filter = ["stream", "region", "shard"]
    readonly_fields = ["region", "stream", "shard"]
