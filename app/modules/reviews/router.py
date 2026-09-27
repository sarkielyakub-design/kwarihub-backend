from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.products.repository import ProductRepository
from app.modules.reviews.repository import ReviewRepository
from app.modules.reviews.schemas import (
    CreateReviewRequest,
    UpdateReviewRequest,
    ReviewResponse,
    ProductReviewResponse,
    ReviewSummaryResponse,
)
from app.modules.reviews.service import ReviewService
from app.modules.users.models import User


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return ReviewService(
        review_repo=ReviewRepository(db),
        product_repo=ProductRepository(db),
    )


@router.post(
    "",
    response_model=ReviewResponse,
)
async def create_review(
    request: CreateReviewRequest,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_service),
):
    return await service.create(
        current_user.id,
        request,
    )


@router.get(
    "/{uuid}",
    response_model=ReviewResponse,
)
async def get_review(
    uuid: str,
    service: ReviewService = Depends(get_service),
):
    return await service.get(uuid)


@router.patch(
    "/{uuid}",
    response_model=ReviewResponse,
)
async def update_review(
    uuid: str,
    request: UpdateReviewRequest,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_service),
):
    return await service.update(
        current_user.id,
        uuid,
        request,
    )


@router.delete("/{uuid}")
async def delete_review(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_service),
):
    return await service.delete(
        current_user.id,
        uuid,
    )


@router.get(
    "/product/{product_uuid}",
    response_model=list[ProductReviewResponse],
)
async def product_reviews(
    product_uuid: str,
    service: ReviewService = Depends(get_service),
):
    return await service.product_reviews(
        product_uuid,
    )


@router.get(
    "/product/{product_uuid}/summary",
    response_model=ReviewSummaryResponse,
)
async def review_summary(
    product_uuid: str,
    service: ReviewService = Depends(get_service),
):
    return await service.summary(
        product_uuid,
    )


@router.get(
    "/seller/me",
    response_model=list[ProductReviewResponse],
)
async def seller_reviews(
    current_user: User = Depends(get_current_user),
    service: ReviewService = Depends(get_service),
):
    return await service.seller_reviews(
        current_user.id,
    )