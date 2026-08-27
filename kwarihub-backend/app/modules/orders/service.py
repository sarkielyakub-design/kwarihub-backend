from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException

from app.modules.cart.repository import CartRepository
from app.modules.order_items.models import OrderItem
from app.modules.order_items.repository import OrderItemRepository
from app.modules.orders.models import Order, OrderStatus
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import CheckoutRequest
from app.modules.payments.monnify import MonnifyClient
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.service import PaymentService
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
        payment_repo: PaymentRepository,
        monnify: MonnifyClient,
    ):
        self.order_repo = order_repo
        self.order_item_repo = order_item_repo
        self.cart_repo = cart_repo
        self.variant_repo = variant_repo
        self.payment_repo = payment_repo
        self.monnify = monnify

    # ============================================================
    # CHECKOUT
    # ============================================================

    async def checkout(
        self,
        user,
        request: CheckoutRequest,
    ):
        # ========================================================
        # GET USER CART
        # ========================================================

        cart_items = await self.cart_repo.get_user_cart(
            user.id
        )

        if not cart_items:
            raise HTTPException(
                status_code=400,
                detail="Your cart is empty.",
            )

        # ========================================================
        # VALIDATE CART + CALCULATE SUBTOTAL
        # ========================================================

        subtotal = Decimal("0.00")

        for item in cart_items:
            variant = item.variant

            if not variant:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "A product variant in your cart "
                        "no longer exists."
                    ),
                )

            if variant.is_deleted or not variant.is_active:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Product variant {variant.sku} "
                        "is unavailable."
                    ),
                )

            if variant.quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Insufficient stock for "
                        f"{variant.sku}."
                    ),
                )

            subtotal += (
                variant.price * item.quantity
            )

        # ========================================================
        # TOTAL
        # ========================================================

        shipping_fee = Decimal("0.00")
        total = subtotal + shipping_fee

        # ========================================================
        # CREATE ORDER
        # ========================================================

        order = Order(
            order_number=(
                f"KWR-{uuid4().hex[:10].upper()}"
            ),
            buyer_id=user.id,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total=total,
            shipping_address=request.shipping_address,
            status=OrderStatus.PENDING,
        )

        await self.order_repo.create(order)

        # ========================================================
        # CREATE ORDER ITEMS
        # ========================================================

        order_items = []

        for item in cart_items:
            variant = item.variant
            product = variant.product

            if not product:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "The product associated with "
                        f"{variant.sku} no longer exists."
                    ),
                )

            variant_name_parts = [
                value
                for value in [
                    variant.color,
                    variant.size,
                    variant.material,
                ]
                if value
            ]

            variant_name = (
                " / ".join(variant_name_parts)
                if variant_name_parts
                else variant.sku
            )

            order_item = OrderItem(
                order_id=order.id,
                product_id=variant.product_id,
                variant_id=variant.id,
                seller_id=product.seller_id,
                product_name=product.name,
                variant_name=variant_name,
                quantity=item.quantity,
                unit_price=variant.price,
                total_price=(
                    variant.price * item.quantity
                ),
            )

            await self.order_item_repo.create(
                order_item
            )

            order_items.append(order_item)

        # ========================================================
        # INITIALIZE MONNIFY PAYMENT
        # ========================================================

        payment_service = PaymentService(
            monnify=self.monnify,
            payment_repo=self.payment_repo,
        )

        payment = await payment_service.initialize(
            order=order,
            customer_name=(
                f"{user.first_name} {user.last_name}"
            ).strip(),
            customer_email=user.email,
            redirect_url=request.redirect_url,
        )

        # ========================================================
        # COMMIT ORDER + ITEMS + PAYMENT
        # ========================================================

        await self.order_repo.commit()
# ========================================================
    # CHECKOUT RESPONSE
    # ========================================================

        return {
        "uuid": order.uuid,
        "order_number": order.order_number,
        "subtotal": order.subtotal,
        "shipping_fee": order.shipping_fee,
        "total": order.total,
        "status": order.status,
        "shipping_address": order.shipping_address,

        "items": [
            {
                "uuid": item.uuid,
                "product_name": item.product_name,
                "variant_name": item.variant_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
            }
            for item in order_items
        ],

        "payment_reference": payment.payment_reference,
        "transaction_reference": payment.transaction_reference,
        "checkout_url": payment.checkout_url,
    }
    # ============================================================
    # MY ORDERS
    # ============================================================

    async def my_orders(
        self,
        user_id: int,
    ):
        return await self.order_repo.get_user_orders(
            user_id
        )

    # ============================================================
    # GET ORDER
    # ============================================================

    async def get_order(
        self,
        uuid: str,
        user_id: int,
    ):
        order = await self.order_repo.get_by_uuid(
            uuid
        )

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

    # ============================================================
    # UPDATE STATUS
    # ============================================================

    async def update_status(
        self,
        uuid: str,
        status: OrderStatus,
    ):
        order = await self.order_repo.get_by_uuid(
            uuid
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        order.status = status

        return await self.order_repo.update(
            order
        )