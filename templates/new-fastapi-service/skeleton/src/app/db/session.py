"""Async SQLAlchemy engine and per-request sessions."""

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine


def to_async_url(url: str) -> str:
    """CloudNativePG gives postgresql://...; SQLAlchemy needs the psycopg (v3) async driver."""
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url.removeprefix(prefix)
    return url


def create_engine(url: str, pool_size: int = 5, max_overflow: int = 5) -> AsyncEngine:
    return create_async_engine(
        to_async_url(url), pool_pre_ping=True, pool_size=pool_size, max_overflow=max_overflow
    )


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.sessionmaker() as session:
        yield session
