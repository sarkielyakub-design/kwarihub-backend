from fastapi import HTTPException, status
from slugify import slugify

from app.core.cache.cache import cache
from app.core.cache.keys import CacheKeys
from app.modules.categories.models import Category
from app.modules.categories.repository import CategoryRepository
from app.modules.categories.schemas import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)


class CategoryService:

    def __init__(
        self,
        repo: CategoryRepository,
    ):
        self.repo = repo

    # ============================================================
    # CREATE
    # ============================================================

    async def create(
        self,
        request: CategoryCreateRequest,
    ) -> Category:

        existing = await self.repo.get_by_name(
            request.name
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists.",
            )

        slug = slugify(
            request.name
        )

        slug_exists = await self.repo.get_by_slug(
            slug
        )

        if slug_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category slug already exists.",
            )

        # --------------------------------------------------------
        # PARENT
        # --------------------------------------------------------

        if request.parent_id is not None:

            parent = await self.repo.db.get(
                Category,
                request.parent_id,
            )

            if not parent or parent.is_deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent category not found.",
                )

        # --------------------------------------------------------
        # CREATE
        # --------------------------------------------------------

        category = Category(
            name=request.name,
            slug=slug,
            description=request.description,
            icon=request.icon,
            parent_id=request.parent_id,
            sort_order=request.sort_order,
            is_featured=request.is_featured,
        )

        category = await self.repo.create(
            category
        )

        # --------------------------------------------------------
        # INVALIDATE CACHE
        # --------------------------------------------------------

        await cache.delete(
            CacheKeys.CATEGORIES
        )

        return category

    # ============================================================
    # GET ALL
    # ============================================================

    async def get_all(
        self,
    ) -> list[CategoryResponse]:

        # --------------------------------------------------------
        # REDIS
        # --------------------------------------------------------

        cached = await cache.get(
            CacheKeys.CATEGORIES
        )

        if cached is not None:

            try:

                return [
                    CategoryResponse.model_validate(
                        item
                    )
                    for item in cached
                ]

            except (
                TypeError,
                ValueError,
            ):
                # Ignore bad cache and rebuild it.
                await cache.delete(
                    CacheKeys.CATEGORIES
                )

        # --------------------------------------------------------
        # DATABASE
        # --------------------------------------------------------

        categories = await self.repo.get_all()

        # --------------------------------------------------------
        # ORM → RESPONSE DATA
        # --------------------------------------------------------

        response_data = [
            CategoryResponse.model_validate(
                category
            ).model_dump(
                mode="json"
            )
            for category in categories
        ]

        # --------------------------------------------------------
        # REDIS
        # --------------------------------------------------------

        await cache.set(
            CacheKeys.CATEGORIES,
            response_data,
            ttl=600,
        )

        # --------------------------------------------------------
        # RETURN
        # --------------------------------------------------------

        return [
            CategoryResponse.model_validate(
                item
            )
            for item in response_data
        ]

    # ============================================================
    # GET BY UUID
    # ============================================================

    async def get_by_uuid(
        self,
        uuid: str,
    ) -> Category:

        category = await self.repo.get_by_uuid(
            uuid
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        return category

    # ============================================================
    # UPDATE
    # ============================================================

    async def update(
        self,
        uuid: str,
        request: CategoryUpdateRequest,
    ):

        category = await self.repo.get_by_uuid(
            uuid
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        data = request.model_dump(
            exclude_unset=True
        )

        # --------------------------------------------------------
        # NAME
        # --------------------------------------------------------

        if "name" in data:

            existing = await self.repo.get_by_name(
                data["name"]
            )

            if (
                existing
                and existing.id != category.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Category name already exists.",
                )

            category.name = data["name"]

            category.slug = slugify(
                data["name"]
            )

        # --------------------------------------------------------
        # OTHER FIELDS
        # --------------------------------------------------------

        for key, value in data.items():

            if key != "name":
                setattr(
                    category,
                    key,
                    value,
                )

        category = await self.repo.update(
            category
        )

        # --------------------------------------------------------
        # INVALIDATE CACHE
        # --------------------------------------------------------

        await cache.delete(
            CacheKeys.CATEGORIES
        )

        return category

    # ============================================================
    # DELETE
    # ============================================================

    async def delete(
        self,
        uuid: str,
    ) -> bool:

        category = await self.repo.get_by_uuid(
            uuid
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        await self.repo.delete(
            category
        )

        # --------------------------------------------------------
        # INVALIDATE CACHE
        # --------------------------------------------------------

        await cache.delete(
            CacheKeys.CATEGORIES
        )

        return True