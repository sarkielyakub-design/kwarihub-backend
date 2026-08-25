from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit_logs.models import AuditLog


class AuditLogRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        log: AuditLog,
    ):
        self.db.add(log)

        await self.db.commit()

        await self.db.refresh(log)

        return log

    async def all(self):
        result = await self.db.execute(
            select(AuditLog)
            .order_by(
                AuditLog.created_at.desc(),
            )
        )

        return result.scalars().all()

    async def get(
        self,
        uuid: str,
    ):
        result = await self.db.execute(
            select(AuditLog).where(
                AuditLog.uuid == uuid,
            )
        )

        return result.scalar_one_or_none()