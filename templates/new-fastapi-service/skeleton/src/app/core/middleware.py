"""Pure ASGI middleware: request id, one JSON access log line and metrics per request."""

import logging
import re
import time
import uuid

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import request_id_var
from app.core.metrics import LATENCY, REQUESTS

logger = logging.getLogger("access")

HEADER = "x-request-id"
_VALID_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
_QUIET_PATHS = frozenset({"/healthz", "/readyz", "/metrics"})


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = next(
            (v.decode("latin-1") for k, v in scope["headers"] if k == HEADER.encode()), ""
        )
        request_id = incoming if _VALID_ID.match(incoming) else uuid.uuid4().hex
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        status = 500

        async def send_with_id(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                MutableHeaders(scope=message)[HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        finally:
            elapsed = time.perf_counter() - start
            path: str = scope["path"]
            route = _route_template(scope)
            REQUESTS.labels(scope["method"], route, str(status)).inc()
            LATENCY.labels(scope["method"], route).observe(elapsed)
            if path not in _QUIET_PATHS:
                logger.info(
                    "request",
                    extra={
                        "method": scope["method"],
                        "path": path,
                        "status": status,
                        "duration_ms": round(elapsed * 1000, 1),
                    },
                )
            request_id_var.reset(token)


def _route_template(scope: Scope) -> str:
    """Route template such as /api/items/{item_id}, to keep metric label cardinality bounded.

    Routers included with a prefix stay nested, so the matched route only knows its own part
    (/items/{item_id}). The prefix is the part of the real path before where the route's own
    pattern matches. Unmatched requests (404) are grouped under one label.
    """
    route = scope.get("route")
    regex = getattr(route, "path_regex", None)
    if route is None or regex is None:
        return "unmatched"
    path: str = scope["path"]
    for i, char in enumerate(path):
        if char == "/" and regex.fullmatch(path[i:]):
            return f"{path[:i]}{route.path}"
    return str(route.path)
