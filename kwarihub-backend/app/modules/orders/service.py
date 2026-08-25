from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException

from app.modules.cart.repository import CartRepository
from app.modules.order_items.models import OrderItem
from app.modules.order_items.repository import OrderItemRepository
from app.modules.orders.models import Order, OrderStatus
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import CheckoutRequest
from app.modules.product_variants.repository import (
    ProductVariantRepository,
)


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        order_item_repo: OrderItemRepository,
        cart_repo: CartRepository,
        variant_repo: ProductVariantRepository,
    ):
        self.order_repo = order_repo
        self.order_item_repo = order_item_repo
        self.cart_repo = cart_repo
        self.variant_repo = variant_repo

    async def checkout(
        self,
        user_id: int,
        request: CheckoutRequest,
    ):
        cart_items = await self.cart_repo.get_user_cart(user_id)

        if not cart_items:
            raise HTTPException(
                status_code=400,
                detail="Your cart is empty.",
            )

        subtotal = Decimal("0.00")

        for item in cart_items:
            variant = item.variant

            if variant.quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {variant.sku}",
                )

            subtotal += variant.price * item.quantity

        shipping_fee = Decimal("0.00")
        total = subtotal + shipping_fee

        order = Order(
            order_number=f"KWR-{uuid4().hex[:10].upper()}",
            buyer_id=user_id,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total=total,
            shipping_address=request.shipping_address,
            status=OrderStatus.PENDING,
        )

        await self.order_repo.create(order)

        for item in cart_items:
            variant = item.variant

            order_item = OrderItem(
                order_id=order.id,
                product_id=variant.product_id,
                variant_id=variant.id,
                seller_id=variant.product.seller_id,
                product_name=variant.product.name,
                variant_name=f"{variant.color} / {variant.size}",
                quantity=item.quantity,
                unit_price=variant.price,
                total_price=variant.price * item.quantity,
            )

            await self.order_item_repo.create(order_item)

            variant.quantity -= item.quantity

            await self.variant_repo.update(variant)

            await self.cart_repo.delete(item)

        await self.order_repo.commit()

        return await self.order_repo.refresh(order)

    async def my_orders(
        self,
        user_id: int,
    ):
        return await self.order_repo.get_user_orders(user_id)

    async def get_order(
        self,
        uuid: str,
        user_id: int,
    ):
        order = await self.order_repo.get_by_uuid(uuid)

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        if order.buyer_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        return order

    async def update_status(
        self,
        uuid: str,
        status: OrderStatus,
    ):
        order = await self.order_repo.get_by_uuid(uuid)

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        order.status = status

        return await self.order_repo.update(order)