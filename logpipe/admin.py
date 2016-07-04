from django.contrib import admin
from . import models


@admin.register(models.Offset)
class OffsetAdmin(admin.ModelAdmin):
    fields = ['topic', 'partition', 'offset']
    list_display = ['topic', 'partition', 'offset']
    list_filter = ['topic', 'partition']
    readonly_fields = ['topic', 'partition']
