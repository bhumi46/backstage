from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for every model (alembic autogenerate reads Base.metadata)."""
