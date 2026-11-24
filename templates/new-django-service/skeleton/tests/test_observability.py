import logging

import pytest
from rest_framework.test import APIClient

from core.logging import RequestIdFilter, request_id_var


def test_generates_request_id(api: APIClient) -> None:
    response = api.get("/healthz")
    assert len(response["X-Request-ID"]) == 32


def test_keeps_valid_incoming_request_id(api: APIClient) -> None:
    response = api.get("/healthz", HTTP_X_REQUEST_ID="abc-123")
    assert response["X-Request-ID"] == "abc-123"


def test_replaces_malformed_request_id(api: APIClient) -> None:
    response = api.get("/healthz", HTTP_X_REQUEST_ID="bad id\nwith newline")
    assert response["X-Request-ID"] != "bad id\nwith newline"


@pytest.mark.django_db
def test_access_log_line(api: APIClient, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="access"):
        api.get("/api/items", HTTP_X_REQUEST_ID="req-1")
    record = next(r for r in caplog.records if r.name == "access")
    assert record.__dict__["status"] == 200
    assert record.__dict__["path"] == "/api/items"


def test_filter_adds_request_id() -> None:
    token = request_id_var.set("req-42")
    try:
        record = logging.LogRecord("x", logging.INFO, __file__, 1, "msg", None, None)
        assert RequestIdFilter().filter(record)
        assert record.__dict__["request_id"] == "req-42"
    finally:
        request_id_var.reset(token)
