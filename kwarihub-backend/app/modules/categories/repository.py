from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.models import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, category: Category) -> Category:
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def get_by_uuid(self, uuid: str) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(
                Category.uuid == uuid,
                Category.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(
                Category.name == name,
                Category.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(
                Category.slug == slug,
                Category.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Category]:
        result = await self.db.execute(
            select(Category)
            .where(Category.is_deleted == False)
            .order_by(Category.sort_order, Category.name)
        )
        return result.scalars().all()

    async def update(self, category: Category) -> Category:
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        category.is_deleted = True
        await self.db.commit()
    async def get_by_id(self, category_id: int):
     return await self.db.get(
        Category,
        category_id,
    )    