"""Business logic for items. Routes call this; it calls the repository."""

from app.repositories.items import ItemRepository
from app.schemas.item import ItemCreate, ItemPage, ItemRead


class ItemNotFoundError(Exception):
    pass


class ItemService:
    def __init__(self, repo: ItemRepository) -> None:
        self.repo = repo

    async def list(self, limit: int, offset: int) -> ItemPage:
        items = await self.repo.list(limit, offset)
        return ItemPage(
            count=await self.repo.count(),
            results=[ItemRead.model_validate(i) for i in items],
        )

    async def get(self, item_id: int) -> ItemRead:
        item = await self.repo.get(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        return ItemRead.model_validate(item)

    async def create(self, data: ItemCreate) -> ItemRead:
        return ItemRead.model_validate(await self.repo.add(data.name))
