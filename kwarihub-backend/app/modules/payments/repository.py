from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.payments.models import Payment


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # CREATE
    # ============================================================

    async def create(
        self,
        payment: Payment,
    ):
        self.db.add(payment)
        await self.db.flush()
        return payment

    # ============================================================
    # GET BY REFERENCE
    # ============================================================

    async def get_by_reference(
        self,
        reference: str,
    ):
        result = await self.db.execute(
            select(Payment)
            .options(
                selectinload(Payment.order)
            )
            .where(
                Payment.reference == reference,
                Payment.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET BY TRANSACTION REFERENCE
    # ============================================================

    async def get_by_transaction_reference(
        self,
        transaction_reference: str,
    ):
        result = await self.db.execute(
            select(Payment)
            .options(
                selectinload(Payment.order)
            )
            .where(
                Payment.transaction_reference
                == transaction_reference,
                Payment.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET BY ORDER ID
    # ============================================================

    async def get_by_order_id(
        self,
        order_id: int,
    ):
        result = await self.db.execute(
            select(Payment)
            .options(
                selectinload(Payment.order)
            )
            .where(
                Payment.order_id == order_id,
                Payment.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET BY UUID
    # ============================================================

    async def get_by_uuid(
        self,
        uuid: str,
    ):
        result = await self.db.execute(
            select(Payment)
            .options(
                selectinload(Payment.order)
            )
            .where(
                Payment.uuid == uuid,
                Payment.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # UPDATE
    # ============================================================

    async def update(
        self,
        payment: Payment,
    ):
        await self.db.flush()
        return payment