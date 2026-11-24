from rest_framework import serializers

from apps.items.models import Item


class ItemSerializer(serializers.ModelSerializer[Item]):
    class Meta:
        model = Item
        fields = ("id", "name", "created_at")
        read_only_fields = ("id", "created_at")
