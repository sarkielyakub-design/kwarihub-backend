from fastapi import HTTPException

from app.modules.notifications.models import Notification
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import (
    CreateNotificationRequest,
)


class NotificationService:

    def __init__(
        self,
        repo: NotificationRepository,
    ):
        self.repo = repo

    async def create(
        self,
        request: CreateNotificationRequest,
    ):
        notification = Notification(
            user_id=request.user_id,
            title=request.title,
            message=request.message,
            type=request.type,
        )

        return await self.repo.create(notification)

    async def get_all(
        self,
        user_id: int,
    ):
        return await self.repo.get_all(user_id)

    async def get_unread(
        self,
        user_id: int,
    ):
        return await self.repo.get_unread(user_id)

    async def count(
        self,
        user_id: int,
    ):
        unread = await self.repo.unread_count(user_id)
        total = await self.repo.total_count(user_id)

        return {
            "unread": unread,
            "total": total,
        }

    async def get(
        self,
        uuid: str,
    ):
        notification = await self.repo.get_by_uuid(uuid)

        if not notification:
            raise HTTPException(
                status_code=404,
                detail="Notification not found.",
            )

        return notification

    async def mark_as_read(
        self,
        user_id: int,
        uuid: str,
    ):
        notification = await self.repo.get_by_uuid(uuid)

        if not notification:
            raise HTTPException(
                status_code=404,
                detail="Notification not found.",
            )

        if notification.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        notification.is_read = True

        return await self.repo.update(notification)

    async def mark_all_as_read(
        self,
        user_id: int,
    ):
        await self.repo.mark_all_as_read(user_id)

        return {
            "success": True,
            "message": "All notifications marked as read.",
        }

    async def delete(
        self,
        user_id: int,
        uuid: str,
    ):
        notification = await self.repo.get_by_uuid(uuid)

        if not notification:
            raise HTTPException(
                status_code=404,
                detail="Notification not found.",
            )

        if notification.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        await self.repo.delete(notification)

        return {
            "success": True,
            "message": "Notification deleted successfully.",
        }