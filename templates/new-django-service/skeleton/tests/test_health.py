from unittest.mock import patch

import pytest
from django.db import DatabaseError
from rest_framework.test import APIClient


def test_healthz(api: APIClient) -> None:
    response = api.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_readyz_ok(api: APIClient) -> None:
    response = api.get("/readyz")
    assert response.status_code == 200


@pytest.mark.django_db
def test_readyz_database_down(api: APIClient) -> None:
    with patch("core.views.connection.cursor", side_effect=DatabaseError("down")):
        response = api.get("/readyz")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


def test_metrics(api: APIClient) -> None:
    response = api.get("/metrics")
    assert response.status_code == 200
    assert b"django_http_requests" in response.content


def test_healthz_rejects_post(api: APIClient) -> None:
    assert api.post("/healthz").status_code == 405
