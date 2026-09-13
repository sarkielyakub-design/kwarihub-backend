from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

from app.modules.categories.repository import CategoryRepository
from app.modules.categories.schemas import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
    MessageResponse,
)
from app.modules.categories.service import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


def get_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    repo = CategoryRepository(db)
    return CategoryService(repo)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    request: CategoryCreateRequest,
    service: CategoryService = Depends(get_service),
):
    return await service.create(request)


@router.get(
    "",
    response_model=List[CategoryResponse],
)
async def get_categories(
    service: CategoryService = Depends(get_service),
):
    return await service.get_all()


@router.get(
    "/{uuid}",
    response_model=CategoryResponse,
)
async def get_category(
    uuid: str,
    service: CategoryService = Depends(get_service),
):
    return await service.get_by_uuid(uuid)


@router.patch(
    "/{uuid}",
    response_model=CategoryResponse,
)
async def update_category(
    uuid: str,
    request: CategoryUpdateRequest,
    service: CategoryService = Depends(get_service),
):
    return await service.update(uuid, request)


@router.delete(
    "/{uuid}",
    response_model=MessageResponse,
)
async def delete_category(
    uuid: str,
    service: CategoryService = Depends(get_service),
):
    return await service.delete(uuid)