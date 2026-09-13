from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.order_items.models import OrderItem


class OrderItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, item: OrderItem):
        self.db.add(item)
        await self.db.flush()
        return item

    async def get_by_uuid(self, uuid: str):
        result = await self.db.execute(
            select(OrderItem).where(
                OrderItem.uuid == uuid,
                OrderItem.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, item_id: int):
        return await self.db.get(
            OrderItem,
            item_id,
        )

    async def update(self, item: OrderItem):
        await self.db.commit()
        await self.db.refresh(item)
        return item