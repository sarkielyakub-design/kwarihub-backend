from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product_variants.models import ProductVariant
from app.modules.products.models import Product


class InventoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        seller_id: int,
    ):
        result = await self.db.execute(
            select(ProductVariant)
            .options(
                selectinload(ProductVariant.product)
            )
            .join(Product)
            .where(
                Product.seller_id == seller_id,
                ProductVariant.is_deleted == False,
            )
            .order_by(Product.name)
        )

        return result.scalars().all()

    async def get_variant(
        self,
        uuid: str,
        seller_id: int,
    ):
        result = await self.db.execute(
            select(ProductVariant)
            .options(
                selectinload(ProductVariant.product)
            )
            .join(Product)
            .where(
                ProductVariant.uuid == uuid,
                Product.seller_id == seller_id,
            )
        )

        return result.scalar_one_or_none()

    async def update(
        self,
        variant,
    ):
        await self.db.commit()
        await self.db.refresh(variant)

        return variant