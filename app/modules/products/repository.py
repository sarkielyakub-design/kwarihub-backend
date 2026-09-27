from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.models import Product


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_all(self) -> list[Product]:
        result = await self.db.execute(
            select(Product)
            .where(Product.is_deleted == False)
            .order_by(Product.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_uuid(self, uuid: str) -> Optional[Product]:
        result = await self.db.execute(
            select(Product).where(
                Product.uuid == uuid,
                Product.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Product]:
        result = await self.db.execute(
            select(Product).where(
                Product.slug == slug,
                Product.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        result = await self.db.execute(
            select(Product).where(
                Product.sku == sku,
                Product.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_seller(self, seller_id: int) -> list[Product]:
        result = await self.db.execute(
            select(Product).where(
                Product.seller_id == seller_id,
                Product.is_deleted == False,
            )
        )
        return result.scalars().all()

    async def update(self, product: Product) -> Product:
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product: Product):
        product.is_deleted = True
        await self.db.commit()