from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.orders.models import OrderStatus
from app.modules.users.models import User
from app.modules.vendors.dependencies import (
    require_approved_vendor,
    require_vendor,
)
from app.modules.vendors.repository import VendorRepository
from app.modules.vendors.schemas import (
    VendorApplicationRequest,
    VendorDashboardResponse,
    VendorOrderItemResponse,
    VendorResponse,
    VendorUpdateRequest,
)
from app.modules.vendors.service import VendorService


router = APIRouter(
    prefix="/seller",
    tags=["Vendor"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
) -> VendorService:

    return VendorService(
        VendorRepository(db),
    )


# ============================================================
# APPLICATION
# ============================================================

@router.post(
    "/application",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    request: VendorApplicationRequest,
    current_user: User = Depends(get_current_user),
    service: VendorService = Depends(get_service),
):
    return await service.create_application(
        current_user,
        request,
    )


@router.get(
    "/application",
    response_model=VendorResponse,
)
async def get_application(
    current_user: User = Depends(get_current_user),
    service: VendorService = Depends(get_service),
):
    return await service.get_application(
        current_user.id,
    )


@router.patch(
    "/application",
    response_model=VendorResponse,
)
async def update_application(
    request: VendorUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: VendorService = Depends(get_service),
):
    return await service.update_application(
        current_user.id,
        request,
    )


# ============================================================
# DASHBOARD
# ============================================================

@router.get(
    "/dashboard",
    response_model=VendorDashboardResponse,
)
async def dashboard(
    vendor=Depends(require_approved_vendor),
    service: VendorService = Depends(get_service),
):
    return await service.dashboard(
        vendor,
    )


# ============================================================
# ORDERS
# ============================================================

@router.get(
    "/orders",
    response_model=list[VendorOrderItemResponse],
)
async def vendor_orders(
    vendor=Depends(require_approved_vendor),
    service: VendorService = Depends(get_service),
):
    return await service.orders(
        vendor.user_id,
    )


@router.get(
    "/orders/{order_item_uuid}",
    response_model=VendorOrderItemResponse,
)
async def vendor_order(
    order_item_uuid: str,
    vendor=Depends(require_approved_vendor),
    service: VendorService = Depends(get_service),
):
    return await service.get_order(
        vendor.user_id,
        order_item_uuid,
    )


@router.patch(
    "/orders/{order_item_uuid}/status",
    response_model=VendorOrderItemResponse,
)
async def update_vendor_order_status(
    order_item_uuid: str,
    order_status: OrderStatus,
    vendor=Depends(require_approved_vendor),
    service: VendorService = Depends(get_service),
):
    return await service.update_order_status(
        seller_id=vendor.user_id,
        item_uuid=order_item_uuid,
        new_status=order_status,
    )