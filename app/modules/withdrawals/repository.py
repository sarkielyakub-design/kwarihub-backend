from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.withdrawals.models import (
    Withdrawal,
    WithdrawalStatus,
)


class WithdrawalRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        withdrawal: Withdrawal,
    ):
        self.db.add(withdrawal)
        await self.db.commit()
        await self.db.refresh(withdrawal)
        return withdrawal

    async def get_by_uuid(
        self,
        uuid: str,
    ):
        result = await self.db.execute(
            select(Withdrawal).where(
                Withdrawal.uuid == uuid,
                Withdrawal.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    async def get_user_withdrawals(
        self,
        user_id: int,
    ):
        result = await self.db.execute(
            select(Withdrawal)
            .where(
                Withdrawal.user_id == user_id,
                Withdrawal.is_deleted == False,
            )
            .order_by(
                Withdrawal.created_at.desc(),
            )
        )

        return result.scalars().all()

    async def get_all(
        self,
    ):
        result = await self.db.execute(
            select(Withdrawal)
            .where(
                Withdrawal.is_deleted == False,
            )
            .order_by(
                Withdrawal.created_at.desc(),
            )
        )

        return result.scalars().all()

    async def pending_total(
        self,
    ):
        return await self.db.scalar(
            select(
                func.coalesce(
                    func.sum(Withdrawal.amount),
                    Decimal("0.00"),
                )
            ).where(
                Withdrawal.status == WithdrawalStatus.PENDING,
                Withdrawal.is_deleted == False,
            )
        )

    async def approved_total(
        self,
    ):
        return await self.db.scalar(
            select(
                func.coalesce(
                    func.sum(Withdrawal.amount),
                    Decimal("0.00"),
                )
            ).where(
                Withdrawal.status == WithdrawalStatus.APPROVED,
                Withdrawal.is_deleted == False,
            )
        )

    async def paid_total(
        self,
    ):
        return await self.db.scalar(
            select(
                func.coalesce(
                    func.sum(Withdrawal.amount),
                    Decimal("0.00"),
                )
            ).where(
                Withdrawal.status == WithdrawalStatus.PAID,
                Withdrawal.is_deleted == False,
            )
        )

    async def rejected_total(
        self,
    ):
        return await self.db.scalar(
            select(
                func.coalesce(
                    func.sum(Withdrawal.amount),
                    Decimal("0.00"),
                )
            ).where(
                Withdrawal.status == WithdrawalStatus.REJECTED,
                Withdrawal.is_deleted == False,
            )
        )

    async def total_count(
        self,
    ):
        return await self.db.scalar(
            select(
                func.count(Withdrawal.id)
            ).where(
                Withdrawal.is_deleted == False,
            )
        ) or 0

    async def update(
        self,
        withdrawal: Withdrawal,
    ):
        await self.db.commit()
        await self.db.refresh(withdrawal)
        return withdrawal

    async def delete(
        self,
        withdrawal: Withdrawal,
    ):
        withdrawal.is_deleted = True
        await self.db.commit()