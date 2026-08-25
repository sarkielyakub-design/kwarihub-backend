from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.schemas import (
    InventoryResponse,
    UpdateInventoryRequest,
    InventoryAdjustmentRequest,
)
from app.modules.inventory.service import InventoryService
from app.modules.users.models import User

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return InventoryService(
        InventoryRepository(db),
    )


@router.get(
    "",
    response_model=list[InventoryResponse],
)
async def inventory(
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(get_service),
):
    return await service.list_inventory(
        current_user.id,
    )


@router.patch(
    "/{variant_uuid}",
    response_model=InventoryResponse,
)
async def update_inventory(
    variant_uuid: str,
    request: UpdateInventoryRequest,
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(get_service),
):
    return await service.update_quantity(
        current_user.id,
        variant_uuid,
        request.quantity,
    )


@router.post(
    "/{variant_uuid}/add-stock",
    response_model=InventoryResponse,
)
async def add_stock(
    variant_uuid: str,
    request: InventoryAdjustmentRequest,
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(get_service),
):
    return await service.add_stock(
        current_user.id,
        variant_uuid,
        request.quantity,
    )