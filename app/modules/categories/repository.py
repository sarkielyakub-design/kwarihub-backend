from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.models import Category
from app.modules.products.models import Product


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, category: Category) -> Category:
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def get_by_uuid(
        self,
        uuid: str,
    ) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(
                Category.uuid == uuid,
                Category.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(
                Category.name == name,
                Category.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        slug: str,
    ) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(
                Category.slug == slug,
                Category.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Category]:
        result = await self.db.execute(
            select(Category)
            .where(Category.is_deleted.is_(False))
            .order_by(
                Category.sort_order,
                Category.name,
            )
        )
        return list(result.scalars().all())

    async def get_all_with_product_counts(
        self,
    ) -> list[tuple[Category, int]]:
        active_product_condition = and_(
            Product.category_id == Category.id,
            Product.is_deleted.is_(False),
            Product.is_active.is_(True),
            Product.status == "active",
        )

        result = await self.db.execute(
            select(
                Category,
                func.count(Product.id).label("product_count"),
            )
            .outerjoin(
                Product,
                active_product_condition,
            )
            .where(
                Category.is_deleted.is_(False),
            )
            .group_by(Category.id)
            .order_by(
                Category.sort_order,
                Category.name,
            )
        )

        return [
            (category, int(product_count or 0))
            for category, product_count in result.all()
        ]

    async def get_product_count(
        self,
        category_id: int,
    ) -> int:
        result = await self.db.execute(
            select(func.count(Product.id)).where(
                Product.category_id == category_id,
                Product.is_deleted.is_(False),
                Product.is_active.is_(True),
                Product.status == "active",
            )
        )
        return int(result.scalar_one() or 0)

    async def get_by_id(
        self,
        category_id: int,
    ) -> Optional[Category]:
        return await self.db.get(
            Category,
            category_id,
        )

    async def update(self, category: Category) -> Category:
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        category.is_deleted = True
        await self.db.commit()