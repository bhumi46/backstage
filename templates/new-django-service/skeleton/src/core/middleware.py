"""Request id propagation and one structured access log line per request."""

import logging
import re
import time
import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from core.logging import request_id_var

logger = logging.getLogger("access")

HEADER = "X-Request-ID"
_VALID_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
_QUIET_PATHS = frozenset({"/healthz", "/readyz", "/metrics"})


class RequestIdMiddleware:
    """Reuses a well-formed incoming X-Request-ID or creates one, and echoes it back."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        incoming = request.headers.get(HEADER, "")
        request_id = incoming if _VALID_ID.match(incoming) else uuid.uuid4().hex
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        try:
            response = self.get_response(request)
            response[HEADER] = request_id
            if request.path not in _QUIET_PATHS:
                logger.info(
                    "request",
                    extra={
                        "method": request.method,
                        "path": request.path,
                        "status": response.status_code,
                        "duration_ms": round((time.perf_counter() - start) * 1000, 1),
                    },
                )
            return response
        finally:
            request_id_var.reset(token)
