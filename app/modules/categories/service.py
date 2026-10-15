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
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    @staticmethod
    def _response(
        category: Category,
        product_count: int = 0,
    ) -> CategoryResponse:
        response = CategoryResponse.model_validate(category)
        return response.model_copy(
            update={"product_count": product_count}
        )

    async def _invalidate_cache(self) -> None:
        await cache.delete(CacheKeys.CATEGORIES)

    async def create(
        self,
        request: CategoryCreateRequest,
    ) -> CategoryResponse:
        existing = await self.repo.get_by_name(request.name)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists.",
            )

        slug = slugify(request.name)
        slug_exists = await self.repo.get_by_slug(slug)

        if slug_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category slug already exists.",
            )

        if request.parent_id is not None:
            parent = await self.repo.get_by_id(request.parent_id)

            if not parent or parent.is_deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent category not found.",
                )

        category = Category(
            name=request.name,
            slug=slug,
            description=request.description,
            icon=request.icon,
            parent_id=request.parent_id,
            sort_order=request.sort_order,
            is_featured=request.is_featured,
        )

        category = await self.repo.create(category)
        await self._invalidate_cache()

        return self._response(category)

    async def get_all(self) -> list[CategoryResponse]:
        cached = await cache.get(CacheKeys.CATEGORIES)

        if cached is not None:
            try:
                if not isinstance(cached, list):
                    raise ValueError("Invalid categories cache.")

                # Older cached responses did not contain product_count.
                if any(
                    not isinstance(item, dict)
                    or "product_count" not in item
                    for item in cached
                ):
                    raise ValueError(
                        "Cached categories are missing product counts."
                    )

                return [
                    CategoryResponse.model_validate(item)
                    for item in cached
                ]

            except (TypeError, ValueError):
                await cache.delete(CacheKeys.CATEGORIES)

        rows = await self.repo.get_all_with_product_counts()

        response_data = [
            self._response(category, product_count).model_dump(
                mode="json"
            )
            for category, product_count in rows
        ]

        await cache.set(
            CacheKeys.CATEGORIES,
            response_data,
            ttl=600,
        )

        return [
            CategoryResponse.model_validate(item)
            for item in response_data
        ]

    async def get_by_uuid(
        self,
        uuid: str,
    ) -> CategoryResponse:
        category = await self.repo.get_by_uuid(uuid)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        product_count = await self.repo.get_product_count(
            category.id
        )

        return self._response(category, product_count)

    async def update(
        self,
        uuid: str,
        request: CategoryUpdateRequest,
    ) -> CategoryResponse:
        category = await self.repo.get_by_uuid(uuid)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        data = request.model_dump(exclude_unset=True)

        if "name" in data and data["name"] is not None:
            existing = await self.repo.get_by_name(data["name"])

            if existing and existing.id != category.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Category name already exists.",
                )

            new_slug = slugify(data["name"])
            slug_existing = await self.repo.get_by_slug(new_slug)

            if slug_existing and slug_existing.id != category.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Category slug already exists.",
                )

            category.name = data.pop("name")
            category.slug = new_slug

        for key, value in data.items():
            setattr(category, key, value)

        category = await self.repo.update(category)
        await self._invalidate_cache()

        product_count = await self.repo.get_product_count(
            category.id
        )

        return self._response(category, product_count)

    async def delete(self, uuid: str) -> bool:
        category = await self.repo.get_by_uuid(uuid)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        await self.repo.delete(category)
        await self._invalidate_cache()

        return True