from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.categories.repository import CategoryRepository
from app.modules.categories.schemas import (
    CategoryCreateRequest,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdateRequest,
    MessageResponse,
)
from app.modules.categories.service import CategoryService


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


# ============================================================
# SERVICE DEPENDENCY
# ============================================================

def get_category_service(
    db: AsyncSession = Depends(get_db),
) -> CategoryService:

    repo = CategoryRepository(db)

    return CategoryService(
        repo=repo
    )


# ============================================================
# GET ALL CATEGORIES
# ============================================================

@router.get(
    "",
    response_model=CategoryListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_categories(
    service: CategoryService = Depends(
        get_category_service
    ),
):

    categories = await service.get_all()

    return CategoryListResponse(
        success=True,
        data=categories,
    )


# ============================================================
# GET CATEGORY
# ============================================================

@router.get(
    "/{uuid}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_category(
    uuid: str,
    service: CategoryService = Depends(
        get_category_service
    ),
):

    return await service.get_by_uuid(
        uuid
    )


# ============================================================
# CREATE CATEGORY
# ============================================================

@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    request: CategoryCreateRequest,
    service: CategoryService = Depends(
        get_category_service
    ),
):

    return await service.create(
        request
    )


# ============================================================
# UPDATE CATEGORY
# ============================================================

@router.patch(
    "/{uuid}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def update_category(
    uuid: str,
    request: CategoryUpdateRequest,
    service: CategoryService = Depends(
        get_category_service
    ),
):

    return await service.update(
        uuid,
        request,
    )


# ============================================================
# DELETE CATEGORY
# ============================================================

@router.delete(
    "/{uuid}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_category(
    uuid: str,
    service: CategoryService = Depends(
        get_category_service
    ),
):

    await service.delete(
        uuid
    )

    return MessageResponse(
        success=True,
        message="Category deleted successfully.",
    )