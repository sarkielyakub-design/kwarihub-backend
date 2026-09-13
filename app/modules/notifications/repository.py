from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, notification: Notification):
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_all(self, user_id: int):
        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_deleted == False,
            )
            .order_by(Notification.created_at.desc())
        )

        return result.scalars().all()

    async def get_by_uuid(self, uuid: str):
        result = await self.db.execute(
            select(Notification).where(
                Notification.uuid == uuid,
                Notification.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    async def get_unread(self, user_id: int):
        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,
                Notification.is_deleted == False,
            )
            .order_by(Notification.created_at.desc())
        )

        return result.scalars().all()

    async def unread_count(self, user_id: int):
        result = await self.db.scalar(
            select(func.count(Notification.id))
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,
                Notification.is_deleted == False,
            )
        )

        return result or 0

    async def total_count(self, user_id: int):
        result = await self.db.scalar(
            select(func.count(Notification.id))
            .where(
                Notification.user_id == user_id,
                Notification.is_deleted == False,
            )
        )

        return result or 0

    async def update(self, notification: Notification):
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def mark_all_as_read(self, user_id: int):
        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
                Notification.is_deleted == False,
            )
        )

        notifications = result.scalars().all()

        for notification in notifications:
            notification.is_read = True

        await self.db.commit()

        return notifications

    async def delete(self, notification: Notification):
        notification.is_deleted = True
        await self.db.commit()