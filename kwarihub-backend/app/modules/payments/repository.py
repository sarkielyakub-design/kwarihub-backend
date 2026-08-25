from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.models import Payment


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payment: Payment):
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def get_by_reference(self, reference: str):
        result = await self.db.execute(
            select(Payment).where(
                Payment.reference == reference,
                Payment.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_order_id(self, order_id: int):
        result = await self.db.execute(
            select(Payment).where(
                Payment.order_id == order_id,
                Payment.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_uuid(self, uuid: str):
        result = await self.db.execute(
            select(Payment).where(
                Payment.uuid == uuid,
                Payment.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, payment: Payment):
        await self.db.commit()
        await self.db.refresh(payment)
        return payment