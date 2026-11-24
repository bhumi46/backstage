from django.contrib import admin

from apps.items.models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin[Item]):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
