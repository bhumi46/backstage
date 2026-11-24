"""JSON logs, one object per line, tagged with the current request id."""

import logging
import logging.config
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Adds the current request id to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def configure_logging(level: str) -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"request_id": {"()": RequestIdFilter}},
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.json.JsonFormatter",
                    "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
                    "rename_fields": {"asctime": "time", "levelname": "level", "name": "logger"},
                },
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "filters": ["request_id"],
                },
            },
            "root": {"handlers": ["stdout"], "level": level.upper()},
            # Requests are logged by RequestContextMiddleware; skip uvicorn's own access log.
            "loggers": {"uvicorn.access": {"level": "WARNING"}},
        }
    )
