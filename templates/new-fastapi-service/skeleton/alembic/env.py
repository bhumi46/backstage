"""Alembic migrations, run online with the async engine. URL from DATABASE_URL."""

import asyncio
import logging

from alembic import context
from sqlalchemy.engine import Connection

import app.models  # noqa: F401  (registers every model on Base.metadata)
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import create_engine

# Same JSON log format as the app, so migration output is visible in the Job's logs.
configure_logging(get_settings().log_level)
logging.getLogger("alembic").setLevel(logging.INFO)

target_metadata = Base.metadata


def run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_engine(get_settings().database_url, pool_size=1, max_overflow=0)
    async with engine.connect() as connection:
        await connection.run_sync(run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    raise SystemExit("offline mode is not supported; set DATABASE_URL and run online")
asyncio.run(run_async_migrations())
