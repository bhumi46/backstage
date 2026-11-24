"""Gunicorn settings for production: uvicorn workers (values can be overridden with env vars)."""

import os
import shutil
from pathlib import Path
from typing import Any

# Prometheus multiprocess mode: every worker writes its metrics here; /metrics aggregates them.
# Set here (not in the image) so other commands such as alembic don't use it.
PROMETHEUS_DIR = os.environ.setdefault("PROMETHEUS_MULTIPROC_DIR", "/tmp/prometheus")  # noqa: S108

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
worker_class = "uvicorn_worker.UvicornWorker"
worker_tmp_dir = "/tmp"  # noqa: S108  (emptyDir; the root filesystem is read-only)
timeout = 30
graceful_timeout = 25
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
accesslog = None  # requests are logged as JSON by app.core.middleware
errorlog = "-"


def on_starting(server: Any) -> None:
    shutil.rmtree(PROMETHEUS_DIR, ignore_errors=True)
    Path(PROMETHEUS_DIR).mkdir(parents=True)


def child_exit(server: Any, worker: Any) -> None:
    from prometheus_client import multiprocess

    multiprocess.mark_process_dead(worker.pid)  # type: ignore[no-untyped-call]  # untyped upstream
