from fastapi import HTTPException, status

from app.modules.audit_logs.models import AuditLog
from app.modules.audit_logs.repository import AuditLogRepository


class AuditLogService:

    def __init__(
        self,
        repo: AuditLogRepository,
    ):
        self.repo = repo

    # ==========================
    # Create Audit Log
    # ==========================

    async def create(
        self,
        log: AuditLog,
    ):
        return await self.repo.create(log)

    # ==========================
    # Get All Audit Logs
    # ==========================

    async def all(self):
        return await self.repo.all()

    # ==========================
    # Get Audit Log
    # ==========================

    async def get(
        self,
        uuid: str,
    ):
        log = await self.repo.get(uuid)

        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit log not found.",
            )

        return log