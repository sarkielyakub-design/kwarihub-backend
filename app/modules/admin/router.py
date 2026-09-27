from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.admin.schemas import MarketplaceAnalyticsResponse
from app.database.session import get_db
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import DashboardResponse
from app.modules.admin.service import AdminService
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return AdminService(
        AdminRepository(db),
    )


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
)
async def dashboard(
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.dashboard()


# ==============================
# Users Management
# ==============================

@router.get("/users")
async def users(
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.users()


@router.get("/users/{uuid}")
async def user(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.user(uuid)


@router.patch("/users/{uuid}/activate")
async def activate_user(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.activate_user(uuid)


@router.patch("/users/{uuid}/deactivate")
async def deactivate_user(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.deactivate_user(uuid)


@router.delete("/users/{uuid}")
async def delete_user(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.delete_user(uuid)
# ==============================
# Seller Management
# ==============================

@router.get("/sellers")
async def sellers(
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.sellers()


@router.get("/sellers/{uuid}")
async def seller(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.seller(uuid)


@router.patch("/sellers/{uuid}/verify")
async def verify_seller(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.verify_seller(uuid)


@router.patch("/sellers/{uuid}/suspend")
async def suspend_seller(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.suspend_seller(uuid)


@router.patch("/sellers/{uuid}/activate")
async def activate_seller(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.activate_seller(uuid)
# ==============================
# Product Management
# ==============================

@router.get("/products")
async def products(
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.products()


@router.get("/products/{uuid}")
async def product(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.product(uuid)


@router.patch("/products/{uuid}/approve")
async def approve_product(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.approve_product(uuid)


@router.patch("/products/{uuid}/reject")
async def reject_product(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.reject_product(uuid)


@router.delete("/products/{uuid}")
async def delete_product(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.delete_product(uuid)
# ==============================
# Order Management
# ==============================

@router.get("/orders")
async def orders(
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.orders()


@router.get("/orders/{uuid}")
async def order(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.order(uuid)


@router.patch("/orders/{uuid}/cancel")
async def cancel_order(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.cancel_order(uuid)
# ==============================
# Payment Management
# ==============================

@router.get("/payments")
async def payments(
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.payments()


@router.get("/payments/{uuid}")
async def payment(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.payment(uuid)
# ==============================
# Withdrawal Management
# ==============================

@router.get("/withdrawals")
async def withdrawals(
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.withdrawals()


@router.get("/withdrawals/{uuid}")
async def withdrawal(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.withdrawal(uuid)


@router.patch("/withdrawals/{uuid}/approve")
async def approve_withdrawal(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.approve_withdrawal(uuid)


@router.patch("/withdrawals/{uuid}/reject")
async def reject_withdrawal(
    uuid: str,
    reason: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.reject_withdrawal(
        uuid,
        reason,
    )


@router.patch("/withdrawals/{uuid}/paid")
async def mark_paid(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.mark_withdrawal_paid(
        uuid,
    )
# ==============================
# Review Management
# ==============================

@router.get("/reviews")
async def reviews(
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.reviews()


@router.get("/reviews/{uuid}")
async def review(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.review(uuid)


@router.patch("/reviews/{uuid}/hide")
async def hide_review(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.hide_review(uuid)


@router.patch("/reviews/{uuid}/show")
async def show_review(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.show_review(uuid)


@router.delete("/reviews/{uuid}")
async def delete_review(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.delete_review(uuid)
@router.get(
    "/analytics",
    response_model=MarketplaceAnalyticsResponse,
)
async def analytics(
    current_user: User = Depends(get_current_user),
    service: AdminService = Depends(get_service),
):
    return await service.analytics()