from django.db.models import QuerySet
from rest_framework import mixins, viewsets

from apps.items.models import Item
from apps.items.serializers import ItemSerializer


class ItemViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet[Item],
):
    """GET/POST /api/items, GET /api/items/{id}."""

    serializer_class = ItemSerializer

    def get_queryset(self) -> QuerySet[Item]:
        return Item.objects.all()
