"""Import every model here so Base.metadata (and alembic) sees it."""

from app.models.item import Item

__all__ = ["Item"]
