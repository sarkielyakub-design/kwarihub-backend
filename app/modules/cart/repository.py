from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.cart.models import CartItem
from app.modules.product_variants.models import ProductVariant
from app.modules.products.models import Product


class CartRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # ================================================================
    # COMMON LOAD OPTIONS
    # ================================================================

    @staticmethod
    def _load_options():
        return (
            selectinload(
                CartItem.variant,
            )
            .selectinload(
                ProductVariant.product,
            )
            .selectinload(
                Product.images,
            )
        )

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
    # ================================================================

    async def get_by_uuid(
        self,
        uuid: str,
    ):
        result = await self.db.execute(
            select(CartItem)
            .options(
                self._load_options()
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
                self._load_options()
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
    # GET USER + VARIANT
    #
    # IMPORTANT:
    # include_deleted=True allows us to find soft-deleted rows.
    # This is necessary because the database UNIQUE constraint still
    # sees those rows.
    # ================================================================

    async def get_user_variant(
        self,
        user_id: int,
        variant_id: int,
        include_deleted: bool = False,
    ):
        conditions = [
            CartItem.user_id == user_id,
            CartItem.variant_id == variant_id,
        ]

        if not include_deleted:
            conditions.append(
                CartItem.is_deleted == False
            )

        result = await self.db.execute(
            select(CartItem)
            .options(
                self._load_options()
            )
            .where(
                *conditions
            )
            .limit(1)
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

    # ================================================================
    # ROLLBACK
    # ================================================================

    async def rollback(self):
        await self.db.rollback()