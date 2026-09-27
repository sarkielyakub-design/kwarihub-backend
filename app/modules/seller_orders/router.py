from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.seller_orders.repository import SellerOrderRepository
from app.modules.seller_orders.schemas import (
    SellerOrderResponse,
    UpdateSellerOrderStatusRequest,
)
from app.modules.seller_orders.service import SellerOrderService
from app.modules.users.models import User

router = APIRouter(
    prefix="/seller/orders",
    tags=["Seller Orders"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return SellerOrderService(
        SellerOrderRepository(db),
    )


@router.get(
    "",
    response_model=list[SellerOrderResponse],
)
async def orders(
    current_user: User = Depends(get_current_user),
    service: SellerOrderService = Depends(get_service),
):
    return await service.list_orders(
        current_user.id,
    )


@router.get(
    "/{order_uuid}",
    response_model=SellerOrderResponse,
)
async def order(
    order_uuid: str,
    current_user: User = Depends(get_current_user),
    service: SellerOrderService = Depends(get_service),
):
    return await service.get_order(
        current_user.id,
        order_uuid,
    )


@router.patch(
    "/{order_uuid}/status",
    response_model=SellerOrderResponse,
)
async def update_status(
    order_uuid: str,
    request: UpdateSellerOrderStatusRequest,
    current_user: User = Depends(get_current_user),
    service: SellerOrderService = Depends(get_service),
):
    return await service.update_status(
        current_user.id,
        order_uuid,
        request.status,
    )