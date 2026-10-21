
from fastapi import HTTPException

from app.modules.orders.models import OrderStatus
from app.modules.seller_orders.repository import SellerOrderRepository
from app.modules.seller_orders.schemas import (
    SellerOrderItemResponse,
    SellerOrderResponse,
    SellerOrderStatus,
)


class SellerOrderService:
    def __init__(self, repo: SellerOrderRepository):
        self.repo = repo

    @staticmethod
    def _to_response(order) -> SellerOrderResponse:
        buyer = order.buyer

        buyer_name = " ".join(
            part
            for part in [
                getattr(buyer, "first_name", None),
                getattr(buyer, "last_name", None),
            ]
            if part
        ).strip()

        if not buyer_name:
            buyer_name = (
                getattr(buyer, "username", None)
                or "Unknown Buyer"
            )

        items = [
            SellerOrderItemResponse.model_validate(item)
            for item in order.items
        ]

        return SellerOrderResponse(
            order_uuid=str(order.uuid),
            order_number=order.order_number,
            buyer_name=buyer_name,
            shipping_address=order.shipping_address,
            status=SellerOrderStatus(order.status.value),
            created_at=order.created_at,
            items=items,
        )

    async def list_orders(self, seller_id: int):
        orders = await self.repo.get_orders(seller_id)
        return [self._to_response(order) for order in orders]

    async def get_order(self, seller_id: int, order_uuid: str):
        order = await self.repo.get_order(order_uuid, seller_id)

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        return self._to_response(order)

    async def update_status(
        self,
        seller_id: int,
        order_uuid: str,
        status: SellerOrderStatus,
    ):
        order = await self.repo.get_order(order_uuid, seller_id)

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        current_status = OrderStatus(order.status.value)

        # Sellers cannot mark an order as paid.
        # Payment verification must handle that transition.
        allowed_transitions = {
            OrderStatus.PAID: {OrderStatus.PROCESSING},
            OrderStatus.PROCESSING: {
                OrderStatus.SHIPPED,
                OrderStatus.CANCELLED,
            },
            OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
        }

        requested_status = OrderStatus(status.value)

        if requested_status not in allowed_transitions.get(
            current_status, set()
        ):
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cannot change order status from "
                    f"{current_status.value} to "
                    f"{requested_status.value}."
                ),
            )

        order.status = requested_status

        try:
            updated_order = await self.repo.update(order)
        except Exception:
            await self.repo.db.rollback()
            raise

        return self._to_response(updated_order)
