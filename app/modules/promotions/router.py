
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.database.models import User
from app.modules.auth.authorization import require_permission
from app.modules.promotions.schemas import (
    PromotionCreate,
    PromotionUpdate,
    PromotionResponse,
)
from app.modules.promotions.service import PromotionService


router = APIRouter(
    prefix="/promotions",
    tags=["Promotions"],
)


# ---------------------------------------------------------
# DEPENDENCIES
# ---------------------------------------------------------

def get_promotion_service(
    db: AsyncSession = Depends(get_db),
) -> PromotionService:
    return PromotionService(db)


# ---------------------------------------------------------
# PUBLIC ENDPOINTS
# ---------------------------------------------------------

@router.get(
    "/active",
    response_model=list[PromotionResponse],
    summary="List active promotions",
)
async def list_active_promotions(
    service: PromotionService = Depends(get_promotion_service),
):
    """Return promotions currently available to customers."""
    return await service.list_active()


@router.get(
    "/{promotion_id}",
    response_model=PromotionResponse,
    summary="Get promotion details",
)
async def get_promotion(
    promotion_id: int,
    service: PromotionService = Depends(get_promotion_service),
):
    """Return a promotion only when it is currently available."""
    promotion = await service.get_by_id(promotion_id)

    if not service.is_currently_available(promotion):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found or unavailable.",
        )

    return promotion


# ---------------------------------------------------------
# ADMIN ENDPOINTS
# Keep /admin/list before /admin/{promotion_id} routes.
# ---------------------------------------------------------

@router.get(
    "/admin/list",
    response_model=list[PromotionResponse],
    summary="List promotions for admin",
)
async def admin_list_promotions(
    current_user: User = Depends(
        require_permission("admin.promotions")
    ),
    service: PromotionService = Depends(get_promotion_service),
):
    """List promotions for authorized administrators."""
    return await service.list_admin()


@router.post(
    "/admin",
    response_model=PromotionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a promotion",
)
async def create_promotion(
    payload: PromotionCreate,
    current_user: User = Depends(
        require_permission("admin.promotions")
    ),
    service: PromotionService = Depends(get_promotion_service),
):
    """Create a promotion."""
    return await service.create(payload)


@router.patch(
    "/admin/{promotion_id}",
    response_model=PromotionResponse,
    summary="Update a promotion",
)
async def update_promotion(
    promotion_id: int,
    payload: PromotionUpdate,
    current_user: User = Depends(
        require_permission("admin.promotions")
    ),
    service: PromotionService = Depends(get_promotion_service),
):
    """Update an existing promotion."""
    return await service.update(promotion_id, payload)


@router.patch(
    "/admin/{promotion_id}/publish",
    response_model=PromotionResponse,
    summary="Publish a promotion",
)
async def publish_promotion(
    promotion_id: int,
    current_user: User = Depends(
        require_permission("admin.promotions")
    ),
    service: PromotionService = Depends(get_promotion_service),
):
    """Publish a promotion."""
    return await service.publish(promotion_id)


@router.patch(
    "/admin/{promotion_id}/pause",
    response_model=PromotionResponse,
    summary="Pause a promotion",
)
async def pause_promotion(
    promotion_id: int,
    current_user: User = Depends(
        require_permission("admin.promotions")
    ),
    service: PromotionService = Depends(get_promotion_service),
):
    """Pause a promotion."""
    return await service.pause(promotion_id)


@router.delete(
    "/admin/{promotion_id}",
    summary="Soft-delete a promotion",
)
async def delete_promotion(
    promotion_id: int,
    current_user: User = Depends(
        require_permission("admin.promotions")
    ),
    service: PromotionService = Depends(get_promotion_service),
):
    """Soft-delete a promotion."""
    return await service.delete(promotion_id)
