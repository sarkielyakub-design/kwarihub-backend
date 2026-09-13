from fastapi import HTTPException, status

from app.modules.products.repository import ProductRepository
from app.modules.wishlist.models import Wishlist
from app.modules.wishlist.repository import WishlistRepository


class WishlistService:
    def __init__(
        self,
        wishlist_repo: WishlistRepository,
        product_repo: ProductRepository,
    ):
        self.wishlist_repo = wishlist_repo
        self.product_repo = product_repo

    async def add(
        self,
        product_uuid: str,
        user_id: int,
    ):
        product_uuid = product_uuid.strip()

        product = await self.product_repo.get_by_uuid(
            product_uuid
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        if product.is_deleted or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product is not available.",
            )

        wishlist = await self.wishlist_repo.get_by_user_and_product(
            user_id=user_id,
            product_id=product.id,
            include_deleted=True,
        )

        if wishlist:
            if not wishlist.is_deleted:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product already in wishlist.",
                )

            return await self.wishlist_repo.restore(wishlist)

        wishlist = Wishlist(
            user_id=user_id,
            product_id=product.id,
        )

        return await self.wishlist_repo.create(wishlist)

    async def get_all(
        self,
        user_id: int,
    ):
        return await self.wishlist_repo.get_user_wishlist(
            user_id=user_id,
        )

    async def remove(
        self,
        product_uuid: str,
        user_id: int,
    ):
        product_uuid = product_uuid.strip()

        product = await self.product_repo.get_by_uuid(
            product_uuid
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        wishlist = await self.wishlist_repo.get_by_user_and_product(
            user_id=user_id,
            product_id=product.id,
        )

        if not wishlist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product is not in your wishlist.",
            )

        await self.wishlist_repo.delete(wishlist)

        return {
            "success": True,
            "message": "Removed from wishlist.",
        }