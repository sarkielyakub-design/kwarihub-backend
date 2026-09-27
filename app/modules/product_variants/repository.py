from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.product_variants.models import ProductVariant
from app.modules.products.models import Product


class ProductVariantRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # ================================================================
    # CREATE
    # ================================================================

    async def create(
        self,
        variant: ProductVariant,
    ):
        self.db.add(variant)

        await self.db.commit()

        return await self.get_by_uuid(
            variant.uuid,
        )

    # ================================================================
    # GET BY UUID
    #
    # Variant
    #   -> Product
    #       -> Images
    # ================================================================

    async def get_by_uuid(
        self,
        uuid: str,
    ):
        result = await self.db.execute(
            select(ProductVariant)
            .options(
                selectinload(
                    ProductVariant.product,
                ).selectinload(
                    Product.images,
                ),
            )
            .where(
                ProductVariant.uuid == uuid,
                ProductVariant.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # ================================================================
    # GET PRODUCT VARIANTS
    # ================================================================

    async def get_product_variants(
        self,
        product_id: int,
    ):
        result = await self.db.execute(
            select(ProductVariant)
            .options(
                selectinload(
                    ProductVariant.product,
                ).selectinload(
                    Product.images,
                ),
            )
            .where(
                ProductVariant.product_id == product_id,
                ProductVariant.is_deleted == False,
            )
        )

        return result.scalars().all()

    # ================================================================
    # GET BY SKU
    # ================================================================

    async def get_by_sku(
        self,
        sku: str,
    ):
        result = await self.db.execute(
            select(ProductVariant)
            .options(
                selectinload(
                    ProductVariant.product,
                ).selectinload(
                    Product.images,
                ),
            )
            .where(
                ProductVariant.sku == sku,
                ProductVariant.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # ================================================================
    # UPDATE
    # ================================================================

    async def update(
        self,
        variant: ProductVariant,
    ):
        await self.db.commit()

        return await self.get_by_uuid(
            variant.uuid,
        )

    # ================================================================
    # DELETE
    # ================================================================

    async def delete(
        self,
        variant: ProductVariant,
    ):
        variant.is_deleted = True

        await self.db.commit()