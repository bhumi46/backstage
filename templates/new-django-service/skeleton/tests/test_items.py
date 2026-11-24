import pytest
from rest_framework.test import APIClient

from apps.items.models import Item

pytestmark = pytest.mark.django_db


def test_create_and_get(api: APIClient) -> None:
    created = api.post("/api/items", {"name": "widget"}, format="json")
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "widget"

    fetched = api.get(f"/api/items/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "widget"


def test_list_is_paginated(api: APIClient) -> None:
    Item.objects.bulk_create([Item(name=f"item-{i}") for i in range(3)])
    response = api.get("/api/items", {"limit": 2})
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 3
    assert [i["name"] for i in body["results"]] == ["item-0", "item-1"]


def test_validation_error(api: APIClient) -> None:
    response = api.post("/api/items", {"name": ""}, format="json")
    assert response.status_code == 400
    assert "name" in response.json()


def test_not_found(api: APIClient) -> None:
    assert api.get("/api/items/999999").status_code == 404


def test_str() -> None:
    assert str(Item(name="widget")) == "widget"
