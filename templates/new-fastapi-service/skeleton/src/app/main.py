"""Application factory: settings, logging, database, middleware and routes."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api.routes import health, items
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.core.metrics import metrics_endpoint
from app.core.middleware import RequestContextMiddleware
from app.db.session import create_engine


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = create_engine(
            settings.database_url, settings.db_pool_size, settings.db_max_overflow
        )
        app.state.engine = engine
        app.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        yield
        await engine.dispose()

    app = FastAPI(title=settings.service_name, version="0.1.0", lifespan=lifespan)
    app.add_middleware(RequestContextMiddleware)
    app.include_router(health.router)
    app.include_router(items.router, prefix="/api")
    app.add_route("/metrics", metrics_endpoint, include_in_schema=False)
    return app


app = create_app()
