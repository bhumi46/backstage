from django.db import models


class Item(models.Model):
    """Example resource. Rename or replace it with your own domain model."""

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        return self.name
