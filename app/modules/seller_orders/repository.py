from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.orders.models import Order
from app.modules.order_items.models import OrderItem


class SellerOrderRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_orders(self, seller_id: int):

        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.buyer),
            )
            .join(OrderItem)
            .where(
                OrderItem.seller_id == seller_id,
                Order.is_deleted == False,
            )
            .distinct()
            .order_by(Order.created_at.desc())
        )

        return result.scalars().all()

    async def get_order(
        self,
        order_uuid: str,
        seller_id: int,
    ):

        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.buyer),
            )
            .join(OrderItem)
            .where(
                Order.uuid == order_uuid,
                OrderItem.seller_id == seller_id,
            )
        )

        return result.scalar_one_or_none()

    async def update(self, order):
        await self.db.commit()
        await self.db.refresh(order)
        return order