from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product_images.models import ProductImage


class ProductImageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, image: ProductImage):
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def get_by_uuid(self, uuid: str):
        result = await self.db.execute(
            select(ProductImage).where(
                ProductImage.uuid == uuid,
                ProductImage.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_product_images(self, product_id: int):
        result = await self.db.execute(
            select(ProductImage)
            .where(
                ProductImage.product_id == product_id,
                ProductImage.is_deleted == False,
            )
            .order_by(ProductImage.sort_order)
        )
        return result.scalars().all()

    async def remove_primary(self, product_id: int):
        result = await self.db.execute(
            select(ProductImage).where(
                ProductImage.product_id == product_id,
                ProductImage.is_primary == True,
                ProductImage.is_deleted == False,
            )
        )

        images = result.scalars().all()

        for image in images:
            image.is_primary = False

        await self.db.commit()

    async def update(self, image: ProductImage):
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def delete(self, image: ProductImage):
        image.is_deleted = True
        await self.db.commit()