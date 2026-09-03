from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.products.models import Product
from app.modules.wishlist.models import Wishlist


class WishlistRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, wishlist: Wishlist) -> Wishlist:
        self.db.add(wishlist)
        await self.db.commit()

        return await self.get_by_id(wishlist.id)

    async def get_by_id(
        self,
        wishlist_id: int,
    ) -> Wishlist | None:
        result = await self.db.execute(
            select(Wishlist)
            .options(
                selectinload(Wishlist.product).selectinload(
                    Product.images
                )
            )
            .where(
                Wishlist.id == wishlist_id,
                Wishlist.is_deleted.is_(False),
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user_and_product(
        self,
        user_id: int,
        product_id: int,
        include_deleted: bool = False,
    ) -> Wishlist | None:
        query = select(Wishlist).where(
            Wishlist.user_id == user_id,
            Wishlist.product_id == product_id,
        )

        if not include_deleted:
            query = query.where(
                Wishlist.is_deleted.is_(False)
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_user_wishlist(
        self,
        user_id: int,
    ) -> list[Wishlist]:
        result = await self.db.execute(
            select(Wishlist)
            .options(
                selectinload(Wishlist.product).selectinload(
                    Product.images
                )
            )
            .where(
                Wishlist.user_id == user_id,
                Wishlist.is_deleted.is_(False),
            )
            .order_by(Wishlist.created_at.desc())
        )

        return list(result.scalars().all())

    async def restore(
        self,
        wishlist: Wishlist,
    ) -> Wishlist:
        wishlist.is_deleted = False

        await self.db.commit()

        return await self.get_by_id(wishlist.id)

    async def delete(
        self,
        wishlist: Wishlist,
    ) -> None:
        wishlist.is_deleted = True

        await self.db.commit()