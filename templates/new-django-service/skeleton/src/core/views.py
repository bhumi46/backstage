"""Kubernetes probes."""

import logging

from django.db import DatabaseError, connection
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def healthz(request: HttpRequest) -> JsonResponse:
    """Liveness: the process is serving requests."""
    return JsonResponse({"status": "ok"})


@require_GET
def readyz(request: HttpRequest) -> JsonResponse:
    """Readiness: the database answers."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        logger.warning("readiness check failed: database unavailable")
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
