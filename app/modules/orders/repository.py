from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.orders.models import Order


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, order: Order):
        self.db.add(order)
        await self.db.flush()
        return order

    async def commit(self):
        await self.db.commit()

    async def refresh(self, order: Order):
        await self.db.refresh(order)
        return order

    async def get_by_uuid(self, uuid: str):
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.payment),
            )
            .where(
                Order.uuid == uuid,
                Order.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    async def get_user_orders(self, buyer_id: int):
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.payment),
            )
            .where(
                Order.buyer_id == buyer_id,
                Order.is_deleted == False,
            )
            .order_by(Order.created_at.desc())
        )

        return result.scalars().all()

    async def update(self, order: Order):
        await self.db.commit()
        await self.db.refresh(order)
        return order