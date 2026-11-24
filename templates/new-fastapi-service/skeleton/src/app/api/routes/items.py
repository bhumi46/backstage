from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import ItemServiceDep
from app.schemas.item import ItemCreate, ItemPage, ItemRead
from app.services.items import ItemNotFoundError

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
async def list_items(
    service: ItemServiceDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ItemPage:
    return await service.list(limit, offset)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_item(data: ItemCreate, service: ItemServiceDep) -> ItemRead:
    return await service.create(data)


@router.get("/{item_id}")
async def get_item(item_id: int, service: ItemServiceDep) -> ItemRead:
    try:
        return await service.get(item_id)
    except ItemNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "item not found") from None
