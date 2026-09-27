from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.product_variants.repository import ProductVariantRepository
from app.modules.product_variants.schemas import (
    ProductVariantCreateRequest,
    ProductVariantUpdateRequest,
    ProductVariantResponse,
    MessageResponse,
)
from app.modules.product_variants.service import ProductVariantService
from app.modules.products.repository import ProductRepository
from app.modules.users.models import User

router = APIRouter(
    prefix="/products",
    tags=["Product Variants"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return ProductVariantService(
        variant_repo=ProductVariantRepository(db),
        product_repo=ProductRepository(db),
    )


@router.post(
    "/{product_uuid}/variants",
    response_model=ProductVariantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_variant(
    product_uuid: str,
    request: ProductVariantCreateRequest,
    current_user: User = Depends(get_current_user),
    service: ProductVariantService = Depends(get_service),
):
    return await service.create(
        product_uuid=product_uuid,
        seller_id=current_user.id,
        request=request,
    )


@router.get(
    "/{product_uuid}/variants",
    response_model=list[ProductVariantResponse],
)
async def get_product_variants(
    product_uuid: str,
    service: ProductVariantService = Depends(get_service),
):
    return await service.get_product_variants(
        product_uuid,
    )


@router.get(
    "/variants/{uuid}",
    response_model=ProductVariantResponse,
)
async def get_variant(
    uuid: str,
    service: ProductVariantService = Depends(get_service),
):
    return await service.get_by_uuid(uuid)


@router.patch(
    "/variants/{uuid}",
    response_model=ProductVariantResponse,
)
async def update_variant(
    uuid: str,
    request: ProductVariantUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: ProductVariantService = Depends(get_service),
):
    return await service.update(
        uuid=uuid,
        seller_id=current_user.id,
        request=request,
    )


@router.delete(
    "/variants/{uuid}",
    response_model=MessageResponse,
)
async def delete_variant(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: ProductVariantService = Depends(get_service),
):
    return await service.delete(
        uuid=uuid,
        seller_id=current_user.id,
    )