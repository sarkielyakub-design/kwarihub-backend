from fastapi import HTTPException

from app.modules.seller_orders.repository import (
    SellerOrderRepository,
)


class SellerOrderService:

    def __init__(
        self,
        repo: SellerOrderRepository,
    ):
        self.repo = repo

    async def list_orders(
        self,
        seller_id: int,
    ):
        return await self.repo.get_orders(
            seller_id,
        )

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

        return order

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

        return await self.repo.update(order)