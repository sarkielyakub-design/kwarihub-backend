
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.products.models import Product


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)

        # Reload images relationship for safe serialization.
        return await self.get_by_uuid(str(product.uuid)) or product

    async def get_all(self) -> list[Product]:
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.images))
            .where(Product.is_deleted.is_(False))
            .order_by(Product.created_at.desc())
        )
        return list(result.scalars().unique().all())

    async def get_by_uuid(self, uuid: str) -> Optional[Product]:
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.images))
            .where(
                Product.uuid == uuid,
                Product.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Product]:
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.images))
            .where(
                Product.slug == slug,
                Product.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.images))
            .where(
                Product.sku == sku,
                Product.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_seller(self, seller_id: int) -> list[Product]:
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.images))
            .where(
                Product.seller_id == seller_id,
                Product.is_deleted.is_(False),
            )
            .order_by(Product.created_at.desc())
        )
        return list(result.scalars().unique().all())

    async def update(self, product: Product) -> Product:
        await self.db.commit()
        await self.db.refresh(product)

        return await self.get_by_uuid(str(product.uuid)) or product

    async def delete(self, product: Product):
        product.is_deleted = True
        await self.db.commit()
