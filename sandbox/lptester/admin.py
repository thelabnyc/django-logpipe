from django.contrib import admin

from . import models


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin[models.Person]):
    fields = ["uuid", "first_name", "last_name"]
    readonly_fields = ["uuid"]
    list_display = ["uuid", "first_name", "last_name"]
