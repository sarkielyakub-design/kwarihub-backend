from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import (
    CreateNotificationRequest,
    NotificationResponse,
    NotificationCountResponse,
)
from app.modules.notifications.service import NotificationService
from app.modules.users.models import User

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return NotificationService(
        NotificationRepository(db),
    )


@router.post(
    "",
    response_model=NotificationResponse,
)
async def create_notification(
    request: CreateNotificationRequest,
    service: NotificationService = Depends(get_service),
):
    return await service.create(request)


@router.get(
    "",
    response_model=list[NotificationResponse],
)
async def get_notifications(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_service),
):
    return await service.get_all(
        current_user.id,
    )


@router.get(
    "/unread",
    response_model=list[NotificationResponse],
)
async def get_unread_notifications(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_service),
):
    return await service.get_unread(
        current_user.id,
    )


@router.get(
    "/count",
    response_model=NotificationCountResponse,
)
async def notification_count(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_service),
):
    return await service.count(
        current_user.id,
    )


@router.get(
    "/{uuid}",
    response_model=NotificationResponse,
)
async def get_notification(
    uuid: str,
    service: NotificationService = Depends(get_service),
):
    return await service.get(uuid)


@router.patch(
    "/{uuid}/read",
    response_model=NotificationResponse,
)
async def mark_as_read(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_service),
):
    return await service.mark_as_read(
        current_user.id,
        uuid,
    )


@router.patch("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_service),
):
    return await service.mark_all_as_read(
        current_user.id,
    )


@router.delete("/{uuid}")
async def delete_notification(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_service),
):
    return await service.delete(
        current_user.id,
        uuid,
    )