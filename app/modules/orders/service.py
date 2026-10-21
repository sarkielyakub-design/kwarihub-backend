
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select

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
from app.modules.promotions.models import Promotion
from app.modules.promotions.redemption_model import PromotionRedemption
from app.modules.promotions.service import PromotionService


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

    async def checkout(self, user, request: CheckoutRequest):
        db = self.order_repo.db

        # --------------------------------------------------------
        # GET USER CART
        # --------------------------------------------------------
        cart_items = await self.cart_repo.get_user_cart(user.id)

        if not cart_items:
            raise HTTPException(
                status_code=400,
                detail="Your cart is empty.",
            )

        # --------------------------------------------------------
        # LOCK AND VALIDATE COUPON
        # --------------------------------------------------------
        coupon_code = request.normalized_coupon_code()
        promotion = None

        if coupon_code:
            promotion = await db.scalar(
                select(Promotion)
                .where(
                    Promotion.coupon_code == coupon_code,
                    Promotion.is_deleted.is_(False),
                )
                .with_for_update()
            )

            if promotion is None:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid coupon code.",
                )

            if promotion.promotion_type != "coupon":
                raise HTTPException(
                    status_code=400,
                    detail="This code is not a coupon.",
                )

            if not PromotionService.is_currently_available(promotion):
                raise HTTPException(
                    status_code=400,
                    detail="This coupon is not currently available.",
                )

        # --------------------------------------------------------
        # VALIDATE CART AND CALCULATE SERVER-SIDE SUBTOTAL
        # --------------------------------------------------------
        subtotal = Decimal("0.00")
        eligible_subtotal = Decimal("0.00")
        validated_items = []

        for item in cart_items:
            variant = item.variant

            if not variant:
                raise HTTPException(
                    status_code=400,
                    detail="A product variant in your cart no longer exists.",
                )

            if variant.is_deleted or not variant.is_active:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product variant {variant.sku} is unavailable.",
                )

            if item.quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid quantity for {variant.sku}.",
                )

            if variant.quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {variant.sku}.",
                )

            product = variant.product

            if not product or product.is_deleted or not product.is_active:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product for {variant.sku} is unavailable.",
                )

            line_total = (
                Decimal(str(variant.price)) * item.quantity
            ).quantize(Decimal("0.01"))

            subtotal += line_total
            validated_items.append(
                (item, variant, product, line_total)
            )

            if promotion:
                # A promotion applies to all products when neither
                # target is set. If both are set, either match qualifies.
                eligible = (
                    promotion.product_id is None
                    and promotion.category_id is None
                )

                if promotion.product_id is not None:
                    eligible = eligible or (
                        product.id == promotion.product_id
                    )

                if promotion.category_id is not None:
                    eligible = eligible or (
                        product.category_id == promotion.category_id
                    )

                if eligible:
                    eligible_subtotal += line_total

        subtotal = subtotal.quantize(Decimal("0.01"))
        eligible_subtotal = eligible_subtotal.quantize(
            Decimal("0.01")
        )

        # --------------------------------------------------------
        # CALCULATE DISCOUNT AND FINAL TOTAL
        # --------------------------------------------------------
        discount_amount = Decimal("0.00")

        if promotion:
            # Recheck the usage limit while holding the coupon row lock.
            if (
                promotion.usage_limit is not None
                and promotion.usage_count >= promotion.usage_limit
            ):
                raise HTTPException(
                    status_code=400,
                    detail="This coupon has reached its usage limit.",
                )

            discount_amount = PromotionService.calculate_discount(
                promotion,
                eligible_subtotal,
            )

        shipping_fee = Decimal("0.00")
        total = (
            subtotal - discount_amount + shipping_fee
        ).quantize(Decimal("0.01"))

        if total <= Decimal("0.00"):
            raise HTTPException(
                status_code=400,
                detail=(
                    "The discounted order total must be greater "
                    "than zero. Free checkout is not supported yet."
                ),
            )

        # --------------------------------------------------------
        # DATABASE WRITE TRANSACTION
        #
        # Any failure in order creation, order items, payment
        # initialization, redemption, or commit triggers rollback.
        # --------------------------------------------------------
        try:
            order = Order(
                order_number=f"KWR-{uuid4().hex[:10].upper()}",
                buyer_id=user.id,
                subtotal=subtotal,
                discount_amount=discount_amount,
                coupon_code=coupon_code if promotion else None,
                promotion_id=promotion.id if promotion else None,
                shipping_fee=shipping_fee,
                total=total,
                shipping_address=request.shipping_address,
                status=OrderStatus.PENDING,
            )

            await self.order_repo.create(order)

            # Create order items.
            order_items = []

            for item, variant, product, line_total in validated_items:
                variant_name_parts = [
                    value
                    for value in (
                        variant.color,
                        variant.size,
                        variant.material,
                    )
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
                    total_price=line_total,
                )

                await self.order_item_repo.create(order_item)
                order_items.append(order_item)

            # Initialize Monnify using the server-calculated total.
            payment_service = PaymentService(
                monnify=self.monnify,
                payment_repo=self.payment_repo,
            )

            payment = await payment_service.initialize(
                order=order,
                customer_name=(
                    f"{user.first_name or ''} "
                    f"{user.last_name or ''}"
                ).strip(),
                customer_email=user.email,
                redirect_url=request.redirect_url,
            )

            # Record coupon redemption in the same database transaction.
            if promotion:
                promotion.usage_count += 1

                redemption = PromotionRedemption(
                    promotion_id=promotion.id,
                    order_id=order.id,
                    buyer_id=user.id,
                    coupon_code=coupon_code,
                    discount_amount=discount_amount,
                )

                db.add(redemption)

            # Commit the order, items, payment, and redemption together.
            await self.order_repo.commit()

        except Exception:
            # Roll back all pending local database changes.
            await db.rollback()
            raise

        # --------------------------------------------------------
        # CHECKOUT RESPONSE
        # --------------------------------------------------------
        return {
            "uuid": order.uuid,
            "order_number": order.order_number,
            "subtotal": order.subtotal,
            "discount_amount": order.discount_amount,
            "coupon_code": order.coupon_code,
            "promotion_id": order.promotion_id,
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
            "amount": payment.amount,
            "currency": payment.currency,
        }

    async def my_orders(self, user_id: int):
        return await self.order_repo.get_user_orders(user_id)

    async def get_order(self, uuid: str, user_id: int):
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

    async def update_status(self, uuid: str, status: OrderStatus):
        order = await self.order_repo.get_by_uuid(uuid)

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        order.status = status
        return await self.order_repo.update(order)
