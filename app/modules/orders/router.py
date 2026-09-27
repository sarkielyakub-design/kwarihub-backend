"""KWARIHUB - orders - router.py"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.cart.repository import CartRepository
from app.modules.order_items.repository import OrderItemRepository
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    CheckoutRequest,
    OrderListResponse,
    OrderResponse,
    UpdateOrderStatusRequest,
)
from app.modules.orders.service import OrderService
from app.modules.payments.monnify import MonnifyClient
from app.modules.payments.repository import PaymentRepository
from app.modules.product_variants.repository import ProductVariantRepository
from app.modules.users.models import User


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


# ============================================================
# SERVICE
# ============================================================

def get_service(
    db: AsyncSession = Depends(get_db),
):
    return OrderService(
        order_repo=OrderRepository(db),
        order_item_repo=OrderItemRepository(db),
        cart_repo=CartRepository(db),
        variant_repo=ProductVariantRepository(db),
        payment_repo=PaymentRepository(db),
        monnify=MonnifyClient(),
    )


# ============================================================
# CHECKOUT
# ============================================================

@router.post(
    "/checkout",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def checkout(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_service),
):
    return await service.checkout(
        current_user,
        request,
    )


# ============================================================
# MY ORDERS
# ============================================================

@router.get(
    "",
    response_model=list[OrderListResponse],
)
async def my_orders(
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_service),
):
    return await service.my_orders(
        current_user.id,
    )


# ============================================================
# GET ORDER
# ============================================================

@router.get(
    "/{order_uuid}",
    response_model=OrderResponse,
)
async def get_order(
    order_uuid: str,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_service),
):
    return await service.get_order(
        order_uuid,
        current_user.id,
    )


# ============================================================
# UPDATE ORDER STATUS
# ============================================================

@router.patch(
    "/{order_uuid}/status",
    response_model=OrderResponse,
)
async def update_status(
    order_uuid: str,
    request: UpdateOrderStatusRequest,
    service: OrderService = Depends(get_service),
):
    return await service.update_status(
        order_uuid,
        request.status,
    )