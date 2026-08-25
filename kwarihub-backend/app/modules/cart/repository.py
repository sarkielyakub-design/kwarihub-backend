from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.cart.models import CartItem
from app.modules.product_variants.models import ProductVariant
from app.modules.products.models import Product


class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ================================================================
    # CREATE
    # ================================================================

    async def create(
        self,
        item: CartItem,
    ):
        self.db.add(item)

        await self.db.commit()

        return await self.get_by_uuid(
            item.uuid,
        )

    # ================================================================
    # GET BY UUID
    #
    # CartItem
    #   -> Variant
    #       -> Product
    #           -> Images
    # ================================================================

    async def get_by_uuid(
        self,
        uuid: str,
    ):
        result = await self.db.execute(
            select(CartItem)
            .options(
                selectinload(
                    CartItem.variant,
                )
                .selectinload(
                    ProductVariant.product,
                )
                .selectinload(
                    Product.images,
                ),
            )
            .where(
                CartItem.uuid == uuid,
                CartItem.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # ================================================================
    # GET USER CART
    # ================================================================

    async def get_user_cart(
        self,
        user_id: int,
    ):
        result = await self.db.execute(
            select(CartItem)
            .options(
                selectinload(
                    CartItem.variant,
                )
                .selectinload(
                    ProductVariant.product,
                )
                .selectinload(
                    Product.images,
                ),
            )
            .where(
                CartItem.user_id == user_id,
                CartItem.is_deleted == False,
            )
            .order_by(
                CartItem.created_at.desc(),
            )
        )

        return result.scalars().all()

    # ================================================================
    # GET USER VARIANT
    #
    # Used when adding an item to cart.
    # ================================================================

    async def get_user_variant(
        self,
        user_id: int,
        variant_id: int,
    ):
        result = await self.db.execute(
            select(CartItem)
            .options(
                selectinload(
                    CartItem.variant,
                )
                .selectinload(
                    ProductVariant.product,
                )
                .selectinload(
                    Product.images,
                ),
            )
            .where(
                CartItem.user_id == user_id,
                CartItem.variant_id == variant_id,
                CartItem.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # ================================================================
    # UPDATE
    # ================================================================

    async def update(
        self,
        item: CartItem,
    ):
        await self.db.commit()

        return await self.get_by_uuid(
            item.uuid,
        )

    # ================================================================
    # DELETE
    # ================================================================

    async def delete(
        self,
        item: CartItem,
    ):
        item.is_deleted = True

        await self.db.commit()

    # ================================================================
    # CLEAR CART
    # ================================================================

    async def clear(
        self,
        user_id: int,
    ):
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.is_deleted == False,
            )
        )

        items = result.scalars().all()

        for item in items:
            item.is_deleted = True

        await self.db.commit()