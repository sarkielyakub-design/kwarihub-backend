from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.audit_logs.repository import AuditLogRepository
from app.modules.audit_logs.schemas import AuditLogResponse
from app.modules.audit_logs.service import AuditLogService
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return AuditLogService(
        AuditLogRepository(db),
    )


@router.get(
    "",
    response_model=list[AuditLogResponse],
)
async def audit_logs(
    current_user: User = Depends(get_current_user),
    service: AuditLogService = Depends(get_service),
):
    return await service.all()


@router.get(
    "/{uuid}",
    response_model=AuditLogResponse,
)
async def audit_log(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: AuditLogService = Depends(get_service),
):
    return await service.get(uuid)