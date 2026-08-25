import json

from fastapi import HTTPException, status
from slugify import slugify

from app.core.cache.cache import cache
from app.core.cache.keys import CacheKeys
from app.modules.categories.models import Category
from app.modules.categories.repository import CategoryRepository
from app.modules.categories.schemas import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
)


class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    async def create(
        self,
        request: CategoryCreateRequest,
    ) -> Category:

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

        if request.parent_id:
            parent = await self.repo.db.get(Category, request.parent_id)
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

        # Clear category cache
        await cache.delete(CacheKeys.CATEGORIES)

        return category

    async def get_all(self):
        cached = await cache.get(CacheKeys.CATEGORIES)

        if cached:
            return json.loads(cached)

        categories = await self.repo.get_all()

        # NOTE:
        # This assumes your repository returns serializable data.
        # If it returns SQLAlchemy models, we'll improve this in the next phase.
        await cache.set(
            CacheKeys.CATEGORIES,
            json.dumps(categories, default=str),
            ttl=600,
        )

        return categories

    async def get_by_uuid(self, uuid: str):
        category = await self.repo.get_by_uuid(uuid)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        return category

    async def update(
        self,
        uuid: str,
        request: CategoryUpdateRequest,
    ):
        category = await self.repo.get_by_uuid(uuid)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        data = request.model_dump(exclude_unset=True)

        if "name" in data:
            existing = await self.repo.get_by_name(data["name"])

            if existing and existing.id != category.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Category name already exists.",
                )

            category.name = data["name"]
            category.slug = slugify(data["name"])

        for key, value in data.items():
            if key != "name":
                setattr(category, key, value)

        category = await self.repo.update(category)

        # Clear category cache
        await cache.delete(CacheKeys.CATEGORIES)

        return category

    async def delete(
        self,
        uuid: str,
    ):
        category = await self.repo.get_by_uuid(uuid)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        await self.repo.delete(category)

        # Clear category cache
        await cache.delete(CacheKeys.CATEGORIES)

        return {
            "success": True,
            "message": "Category deleted successfully.",
        }