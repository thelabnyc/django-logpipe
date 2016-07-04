from django.db import models


class Offset(models.Model):
    topic = models.CharField(max_length=200)
    partition = models.PositiveIntegerField()
    offset = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('topic', 'partition')
        ordering = ('topic', 'partition', 'offset')
