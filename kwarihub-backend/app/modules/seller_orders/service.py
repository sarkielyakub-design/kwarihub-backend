from fastapi import HTTPException

from app.modules.seller_orders.repository import SellerOrderRepository
from app.modules.seller_orders.schemas import (
    SellerOrderItemResponse,
    SellerOrderResponse,
)


class SellerOrderService:
    def __init__(
        self,
        repo: SellerOrderRepository,
    ):
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
            buyer_name = getattr(buyer, "username", None) or "Unknown Buyer"

        items = [
            SellerOrderItemResponse.model_validate(item)
            for item in order.items
        ]

        return SellerOrderResponse(
            order_uuid=str(order.uuid),
            order_number=order.order_number,
            buyer_name=buyer_name,
            shipping_address=order.shipping_address,
            status=order.status,
            created_at=order.created_at,
            items=items,
        )

    async def list_orders(
        self,
        seller_id: int,
    ):
        orders = await self.repo.get_orders(seller_id)

        return [
            self._to_response(order)
            for order in orders
        ]

    async def get_order(
        self,
        seller_id: int,
        order_uuid: str,
    ):
        order = await self.repo.get_order(
            order_uuid,
            seller_id,
        )

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
        status,
    ):
        order = await self.repo.get_order(
            order_uuid,
            seller_id,
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        order.status = status

        updated_order = await self.repo.update(order)

        return self._to_response(updated_order)
