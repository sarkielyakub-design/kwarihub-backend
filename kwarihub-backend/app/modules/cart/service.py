from decimal import Decimal

from fastapi import HTTPException

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
            "uuid": item.uuid,
            "user_id": item.user_id,
            "variant_id": item.variant_id,
            "quantity": item.quantity,

            # Product
            "product_id": product.id,
            "product_uuid": product.uuid,
            "product_name": product.name,
            "product_slug": product.slug,

            # Product image
            "product_image": self._product_image(product),

            # Variant
            "variant_uuid": variant.uuid,
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

        # Primary image first
        for image in images:
            if (
                not getattr(image, "is_deleted", False)
                and getattr(image, "is_primary", False)
            ):
                return getattr(
                    image,
                    "image",
                    None,
                )

        # Otherwise first available image
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
    # ADD
    # ================================================================

    async def add(
        self,
        user_id: int,
        request: AddToCartRequest,
    ):
        variant = await self.variant_repo.get_by_uuid(
            request.variant_uuid,
        )

        if not variant:
            raise HTTPException(
                status_code=404,
                detail="Variant not found.",
            )

        if not variant.is_active:
            raise HTTPException(
                status_code=400,
                detail="This variant is not available.",
            )

        if request.quantity < 1:
            raise HTTPException(
                status_code=400,
                detail="Quantity must be at least 1.",
            )

        if variant.quantity < request.quantity:
            raise HTTPException(
                status_code=400,
                detail="Insufficient stock.",
            )

        item = await self.cart_repo.get_user_variant(
            user_id,
            variant.id,
        )

        # ------------------------------------------------------------
        # Existing cart item
        # ------------------------------------------------------------

        if item:
            new_quantity = (
                item.quantity
                + request.quantity
            )

            if new_quantity > variant.quantity:
                raise HTTPException(
                    status_code=400,
                    detail="Insufficient stock.",
                )

            item.quantity = new_quantity

            item = await self.cart_repo.update(
                item,
            )

            return self._item_response(
                item,
            )

        # ------------------------------------------------------------
        # New cart item
        # ------------------------------------------------------------

        item = CartItem(
            user_id=user_id,
            variant_id=variant.id,
            quantity=request.quantity,
        )

        item = await self.cart_repo.create(
            item,
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

        return {
            "items": response_items,
            "subtotal": subtotal,
            "total_items": total_items,
        }

    # ================================================================
    # UPDATE
    # ================================================================

    async def update(
        self,
        cart_uuid: str,
        user_id: int,
        request: UpdateCartRequest,
    ):
        item = await self.cart_repo.get_by_uuid(
            cart_uuid,
        )

        if not item:
            raise HTTPException(
                status_code=404,
                detail="Cart item not found.",
            )

        if item.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        if not item.variant.is_active:
            raise HTTPException(
                status_code=400,
                detail="This variant is no longer available.",
            )

        if request.quantity < 1:
            raise HTTPException(
                status_code=400,
                detail="Quantity must be at least 1.",
            )

        if request.quantity > item.variant.quantity:
            raise HTTPException(
                status_code=400,
                detail="Insufficient stock.",
            )

        item.quantity = request.quantity

        item = await self.cart_repo.update(
            item,
        )

        return self._item_response(
            item,
        )

    # ================================================================
    # REMOVE
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
                status_code=404,
                detail="Cart item not found.",
            )

        if item.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        await self.cart_repo.delete(
            item,
        )

        return {
            "success": True,
            "message": "Item removed from cart.",
        }

    # ================================================================
    # CLEAR
    # ================================================================

    async def clear(
        self,
        user_id: int,
    ):
        await self.cart_repo.clear(
            user_id,
        )

        return {
            "success": True,
            "message": "Cart cleared successfully.",
        }