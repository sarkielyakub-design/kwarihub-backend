from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.cache.cache import cache
from app.core.cache.keys import CacheKeys

from app.modules.cart.models import CartItem
from app.modules.cart.repository import CartRepository
from app.modules.cart.schemas import (
    AddToCartRequest,
    UpdateCartRequest,
)

from app.modules.product_variants.repository import (
    ProductVariantRepository,
)


class CartService:
    def __init__(
        self,
        cart_repo: CartRepository,
        variant_repo: ProductVariantRepository,
    ):
        self.cart_repo = cart_repo
        self.variant_repo = variant_repo

    # ================================================================
    # CACHE
    # ================================================================

    def _cart_cache_key(
        self,
        user_id: int,
    ) -> str:
        return CacheKeys.CART.format(user_id)

    async def _clear_cart_cache(
        self,
        user_id: int,
    ):
        await cache.delete(
            self._cart_cache_key(user_id)
        )

    # ================================================================
    # CART ITEM RESPONSE
    # ================================================================

    def _item_response(
        self,
        item: CartItem,
    ) -> dict:
        variant = item.variant
        product = variant.product

        return {
            "id": item.id,
            "uuid": str(item.uuid),
            "user_id": item.user_id,
            "variant_id": item.variant_id,
            "quantity": item.quantity,

            # Product
            "product_id": product.id,
            "product_uuid": str(product.uuid),
            "product_name": product.name,
            "product_slug": product.slug,

            # Product image
            "product_image": self._product_image(
                product
            ),

            # Variant
            "variant_uuid": str(variant.uuid),
            "color": variant.color,
            "size": variant.size,
            "material": variant.material,
            "variant_sku": variant.sku,

            # Pricing
            "unit_price": variant.price,

            "item_total": (
                variant.price * item.quantity
            ),
        }

    # ================================================================
    # PRODUCT IMAGE
    # ================================================================

    def _product_image(
        self,
        product,
    ):
        images = getattr(
            product,
            "images",
            None,
        )

        if not images:
            return None

        # ------------------------------------------------------------
        # PRIMARY IMAGE
        # ------------------------------------------------------------

        for image in images:
            if (
                not getattr(
                    image,
                    "is_deleted",
                    False,
                )
                and getattr(
                    image,
                    "is_primary",
                    False,
                )
            ):
                return getattr(
                    image,
                    "image",
                    None,
                )

        # ------------------------------------------------------------
        # FIRST AVAILABLE IMAGE
        # ------------------------------------------------------------

        for image in images:
            if not getattr(
                image,
                "is_deleted",
                False,
            ):
                return getattr(
                    image,
                    "image",
                    None,
                )

        return None

    # ================================================================
    # ADD TO CART
    # ================================================================

    async def add(
        self,
        user_id: int,
        request: AddToCartRequest,
    ):
        # ------------------------------------------------------------
        # VALIDATE QUANTITY
        # ------------------------------------------------------------

        if request.quantity < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be at least 1.",
            )

        # ------------------------------------------------------------
        # FIND VARIANT
        # ------------------------------------------------------------

        variant = await self.variant_repo.get_by_uuid(
            request.variant_uuid,
        )

        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Variant not found.",
            )

        # ------------------------------------------------------------
        # CHECK VARIANT STATUS
        # ------------------------------------------------------------

        if not variant.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This variant is not available.",
            )

        # ------------------------------------------------------------
        # CHECK STOCK
        # ------------------------------------------------------------

        if variant.quantity < request.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock.",
            )

        # ------------------------------------------------------------
        # FIND EXISTING CART ITEM
        #
        # IMPORTANT:
        # This also searches soft-deleted items.
        # ------------------------------------------------------------

        item = await self.cart_repo.get_user_variant(
            user_id=user_id,
            variant_id=variant.id,
            include_deleted=True,
        )

        # ============================================================
        # EXISTING CART ITEM
        # ============================================================

        if item:

            # --------------------------------------------------------
            # RESTORE SOFT-DELETED ITEM
            # --------------------------------------------------------

            if item.is_deleted:
                if request.quantity > variant.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Insufficient stock.",
                    )

                item.is_deleted = False
                item.quantity = request.quantity

                item = await self.cart_repo.update(
                    item,
                )

                await self._clear_cart_cache(
                    user_id,
                )

                return self._item_response(
                    item,
                )

            # --------------------------------------------------------
            # ACTIVE ITEM → INCREASE QUANTITY
            # --------------------------------------------------------

            new_quantity = (
                item.quantity
                + request.quantity
            )

            if new_quantity > variant.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient stock.",
                )

            item.quantity = new_quantity

            item = await self.cart_repo.update(
                item,
            )

            await self._clear_cart_cache(
                user_id,
            )

            return self._item_response(
                item,
            )

        # ============================================================
        # NEW CART ITEM
        # ============================================================

        item = CartItem(
            user_id=user_id,
            variant_id=variant.id,
            quantity=request.quantity,
        )

        try:
            item = await self.cart_repo.create(
                item,
            )

        except IntegrityError:
            # --------------------------------------------------------
            # CONCURRENT REQUEST PROTECTION
            #
            # If two requests arrive at exactly the same time,
            # PostgreSQL may allow one INSERT and reject the other.
            # Roll back and retrieve the row that now exists.
            # --------------------------------------------------------

            await self.cart_repo.rollback()

            existing = await self.cart_repo.get_user_variant(
                user_id=user_id,
                variant_id=variant.id,
                include_deleted=True,
            )

            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Unable to add this item to cart. "
                        "Please try again."
                    ),
                )

            if existing.is_deleted:
                existing.is_deleted = False
                existing.quantity = request.quantity
            else:
                new_quantity = (
                    existing.quantity
                    + request.quantity
                )

                if new_quantity > variant.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Insufficient stock.",
                    )

                existing.quantity = new_quantity

            item = await self.cart_repo.update(
                existing,
            )

        await self._clear_cart_cache(
            user_id,
        )

        return self._item_response(
            item,
        )

    # ================================================================
    # GET CART
    # ================================================================

    async def get_cart(
        self,
        user_id: int,
    ):
        cache_key = self._cart_cache_key(
            user_id
        )

        # ------------------------------------------------------------
        # CACHE
        # ------------------------------------------------------------

        cached = await cache.get(
            cache_key
        )

        if cached is not None:
            return cached

        # ------------------------------------------------------------
        # DATABASE
        # ------------------------------------------------------------

        items = await self.cart_repo.get_user_cart(
            user_id,
        )

        subtotal = Decimal("0.00")
        total_items = 0

        response_items = []

        for item in items:
            subtotal += (
                item.variant.price
                * item.quantity
            )

            total_items += item.quantity

            response_items.append(
                self._item_response(
                    item,
                )
            )

        response = {
            "items": response_items,
            "subtotal": subtotal,
            "total_items": total_items,
        }

        # ------------------------------------------------------------
        # CACHE
        # ------------------------------------------------------------

        await cache.set(
            cache_key,
            response,
            ttl=300,
        )

        return response

    # ================================================================
    # UPDATE CART
    # ================================================================

    async def update(
        self,
        cart_uuid: str,
        user_id: int,
        request: UpdateCartRequest,
    ):
        # ------------------------------------------------------------
        # VALIDATE QUANTITY
        # ------------------------------------------------------------

        if request.quantity < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be at least 1.",
            )

        # ------------------------------------------------------------
        # FIND ITEM
        # ------------------------------------------------------------

        item = await self.cart_repo.get_by_uuid(
            cart_uuid,
        )

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found.",
            )

        # ------------------------------------------------------------
        # OWNERSHIP
        # ------------------------------------------------------------

        if item.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized.",
            )

        # ------------------------------------------------------------
        # VARIANT STATUS
        # ------------------------------------------------------------

        if not item.variant.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This variant is no longer available.",
            )

        # ------------------------------------------------------------
        # STOCK
        # ------------------------------------------------------------

        if request.quantity > item.variant.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock.",
            )

        # ------------------------------------------------------------
        # UPDATE
        # ------------------------------------------------------------

        item.quantity = request.quantity

        item = await self.cart_repo.update(
            item,
        )

        await self._clear_cart_cache(
            user_id,
        )

        return self._item_response(
            item,
        )

    # ================================================================
    # REMOVE ITEM
    # ================================================================

    async def remove(
        self,
        cart_uuid: str,
        user_id: int,
    ):
        item = await self.cart_repo.get_by_uuid(
            cart_uuid,
        )

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found.",
            )

        if item.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized.",
            )

        await self.cart_repo.delete(
            item,
        )

        await self._clear_cart_cache(
            user_id,
        )

        return {
            "success": True,
            "message": "Item removed from cart.",
        }

    # ================================================================
    # CLEAR CART
    # ================================================================

    async def clear(
        self,
        user_id: int,
    ):
        await self.cart_repo.clear(
            user_id,
        )

        await self._clear_cart_cache(
            user_id,
        )

        return {
            "success": True,
            "message": "Cart cleared successfully.",
        }