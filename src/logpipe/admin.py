from django.contrib import admin
from . import models


@admin.register(models.KafkaOffset)
class KafkaOffsetAdmin(admin.ModelAdmin):
    fields = ['topic', 'partition', 'offset']
    list_display = ['topic', 'partition', 'offset']
    list_filter = ['topic', 'partition']
    readonly_fields = ['topic', 'partition']
