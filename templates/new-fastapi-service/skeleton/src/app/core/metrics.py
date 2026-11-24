"""Prometheus metrics. Works with one process or many gunicorn workers (multiprocess mode)."""

import os

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    multiprocess,
)
from starlette.requests import Request
from starlette.responses import Response

REQUESTS = Counter(
    "http_requests_total",
    "HTTP requests by method, route template and status.",
    ["method", "route", "status"],
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency by method and route template.",
    ["method", "route"],
)


async def metrics_endpoint(request: Request) -> Response:
    registry = REGISTRY
    if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)  # type: ignore[no-untyped-call]
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
