from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.schemas import (
    SettingsResponse,
    UpdateSettingsRequest,
)
from app.modules.settings.service import SettingsService
from app.modules.users.models import User

router = APIRouter(
    prefix="/settings",
    tags=["Marketplace Settings"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return SettingsService(
        SettingsRepository(db),
    )


@router.get(
    "",
    response_model=SettingsResponse,
)
async def get_settings(
    current_user: User = Depends(get_current_user),
    service: SettingsService = Depends(get_service),
):
    return await service.get()


@router.put(
    "",
    response_model=SettingsResponse,
)
async def update_settings(
    request: UpdateSettingsRequest,
    current_user: User = Depends(get_current_user),
    service: SettingsService = Depends(get_service),
):
    return await service.update(request)