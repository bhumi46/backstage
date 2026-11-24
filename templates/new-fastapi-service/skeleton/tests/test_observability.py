import logging
import os
from unittest.mock import patch

import httpx
import pytest

from app.core.logging import RequestIdFilter, request_id_var
from app.db.session import to_async_url


async def test_generates_request_id(client: httpx.AsyncClient) -> None:
    response = await client.get("/healthz")
    assert len(response.headers["x-request-id"]) == 32


async def test_keeps_valid_incoming_request_id(client: httpx.AsyncClient) -> None:
    response = await client.get("/healthz", headers={"X-Request-ID": "abc-123"})
    assert response.headers["x-request-id"] == "abc-123"


async def test_replaces_malformed_request_id(client: httpx.AsyncClient) -> None:
    response = await client.get("/healthz", headers={"X-Request-ID": "bad id with spaces"})
    assert response.headers["x-request-id"] != "bad id with spaces"


async def test_access_log_line(client: httpx.AsyncClient, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="access"):
        await client.get("/api/items")
    record = next(r for r in caplog.records if r.name == "access")
    assert record.__dict__["status"] == 200
    assert record.__dict__["path"] == "/api/items"


async def test_metrics_multiprocess_mode(
    client: httpx.AsyncClient, tmp_path: os.PathLike[str]
) -> None:
    with patch.dict(os.environ, {"PROMETHEUS_MULTIPROC_DIR": str(tmp_path)}):
        response = await client.get("/metrics")
    assert response.status_code == 200


def test_filter_adds_request_id() -> None:
    token = request_id_var.set("req-42")
    try:
        record = logging.LogRecord("x", logging.INFO, __file__, 1, "msg", None, None)
        assert RequestIdFilter().filter(record)
        assert record.__dict__["request_id"] == "req-42"
    finally:
        request_id_var.reset(token)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("postgresql://u:p@h:5432/db", "postgresql+psycopg://u:p@h:5432/db"),
        ("postgres://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql+psycopg://u@h/db", "postgresql+psycopg://u@h/db"),
    ],
)
def test_to_async_url(url: str, expected: str) -> None:
    assert to_async_url(url) == expected
