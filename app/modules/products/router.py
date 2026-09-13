from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

from app.modules.auth.dependencies import get_current_user
from app.modules.categories.repository import CategoryRepository
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    MessageResponse,
)
from app.modules.products.service import ProductService
from app.modules.users.models import User

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    product_repo = ProductRepository(db)
    category_repo = CategoryRepository(db)

    return ProductService(
        repo=product_repo,
        category_repo=category_repo,
    )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    request: ProductCreateRequest,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_service),
):
    return await service.create(
        seller_id=current_user.id,
        request=request,
    )


@router.get(
    "",
    response_model=List[ProductResponse],
)
async def get_products(
    service: ProductService = Depends(get_service),
):
    return await service.get_all()


@router.get(
    "/my-products",
    response_model=List[ProductResponse],
)
async def my_products(
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_service),
):
    return await service.my_products(
        current_user.id,
    )

@router.get(
    "/{uuid}",
    response_model=ProductResponse,
)
async def get_product(
    uuid: str,
    service: ProductService = Depends(get_service),
):
    product = await service.get_by_uuid(uuid)

    return ProductResponse.model_validate(product)

@router.patch(
    "/{uuid}",
    response_model=ProductResponse,
)
async def update_product(
    uuid: str,
    request: ProductUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_service),
):
    return await service.update(
        uuid=uuid,
        seller_id=current_user.id,
        request=request,
    )


@router.delete(
    "/{uuid}",
    response_model=MessageResponse,
)
async def delete_product(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_service),
):
    return await service.delete(
        uuid=uuid,
        seller_id=current_user.id,
    )