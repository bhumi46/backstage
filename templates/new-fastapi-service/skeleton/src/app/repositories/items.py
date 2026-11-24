"""Database access for items (no HTTP or business rules here)."""

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item


class ItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count(self) -> int:
        return (await self.session.scalar(select(func.count()).select_from(Item))) or 0

    async def list(self, limit: int, offset: int) -> Sequence[Item]:
        result = await self.session.scalars(
            select(Item).order_by(Item.id).limit(limit).offset(offset)
        )
        return result.all()

    async def get(self, item_id: int) -> Item | None:
        return await self.session.get(Item, item_id)

    async def add(self, name: str) -> Item:
        item = Item(name=name)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item
