from unittest.mock import patch

import httpx
from sqlalchemy.exc import OperationalError


async def test_healthz(client: httpx.AsyncClient) -> None:
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readyz_ok(client: httpx.AsyncClient) -> None:
    assert (await client.get("/readyz")).status_code == 200


async def test_readyz_database_down(client: httpx.AsyncClient) -> None:
    error = OperationalError("SELECT 1", {}, Exception("down"))
    with patch("sqlalchemy.ext.asyncio.AsyncConnection.execute", side_effect=error):
        response = await client.get("/readyz")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


async def test_metrics(client: httpx.AsyncClient) -> None:
    await client.get("/api/items")
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert 'route="/api/items"' in response.text
