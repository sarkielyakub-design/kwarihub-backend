from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.wishlist.models import Wishlist


class WishlistRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, wishlist: Wishlist):
        self.db.add(wishlist)
        await self.db.commit()
        await self.db.refresh(wishlist)
        return wishlist

    async def get_by_user_and_product(
        self,
        user_id: int,
        product_id: int,
    ):
        result = await self.db.execute(
            select(Wishlist).where(
                Wishlist.user_id == user_id,
                Wishlist.product_id == product_id,
                Wishlist.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_wishlist(
        self,
        user_id: int,
    ):
        result = await self.db.execute(
            select(Wishlist).where(
                Wishlist.user_id == user_id,
                Wishlist.is_deleted == False,
            )
        )
        return result.scalars().all()

    async def delete(
        self,
        wishlist: Wishlist,
    ):
        wishlist.is_deleted = True
        await self.db.commit()