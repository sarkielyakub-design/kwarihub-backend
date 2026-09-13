from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.dashboard.repository import (
    DashboardRepository,
)
from app.modules.dashboard.schemas import (
    DashboardResponse,
)
from app.modules.dashboard.service import (
    DashboardService,
)
from app.modules.users.models import User


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
) -> DashboardService:

    return DashboardService(
        repo=DashboardRepository(db)
    )


@router.get(
    "",
    response_model=DashboardResponse,
)
async def get_dashboard(
    current_user: User = Depends(
        get_current_user
    ),
    service: DashboardService = Depends(
        get_service
    ),
):
    return await service.get_dashboard(
        current_user.id
    )