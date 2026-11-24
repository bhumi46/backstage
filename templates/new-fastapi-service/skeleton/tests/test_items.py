import httpx


async def test_create_and_get(client: httpx.AsyncClient) -> None:
    created = await client.post("/api/items", json={"name": "widget"})
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "widget"

    fetched = await client.get(f"/api/items/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "widget"


async def test_list_is_paginated(client: httpx.AsyncClient) -> None:
    for i in range(3):
        await client.post("/api/items", json={"name": f"item-{i}"})
    response = await client.get("/api/items", params={"limit": 2})
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 3
    assert [i["name"] for i in body["results"]] == ["item-0", "item-1"]


async def test_validation_error(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/items", json={"name": ""})
    assert response.status_code == 422


async def test_not_found(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/items/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "item not found"}


async def test_limit_bounds(client: httpx.AsyncClient) -> None:
    assert (await client.get("/api/items", params={"limit": 0})).status_code == 422
