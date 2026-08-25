from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==========================
    # Get By ID
    # ==========================

    async def get_by_id(self, user_id: int):
        return await self.db.scalar(
            select(User).where(
                User.id == user_id,
            )
        )

    # ==========================
    # Get By UUID
    # ==========================

    async def get_by_uuid(self, uuid: str):
        return await self.db.scalar(
            select(User).where(
                User.uuid == uuid,
            )
        )

    # ==========================
    # Get By Email
    # ==========================

    async def get_by_email(self, email: str):
        return await self.db.scalar(
            select(User).where(
                User.email == email,
            )
        )

    # ==========================
    # Get By Username
    # ==========================

    async def get_by_username(self, username: str):
        return await self.db.scalar(
            select(User).where(
                User.username == username,
            )
        )

    # ==========================
    # Update
    # ==========================

    async def update(self, user: User):
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # ==========================
    # Change Password
    # ==========================

    async def change_password(self, user: User):
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # ==========================
    # Update Avatar
    # ==========================

    async def update_avatar(self, user: User):
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # ==========================
    # Soft Delete
    # ==========================

    async def soft_delete(self, user: User):
        user.is_deleted = True
        user.is_active = False
        user.deleted_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(user)

        return user

    # ==========================
    # Deactivate
    # ==========================

    async def deactivate(self, user: User):
        user.is_active = False

        await self.db.commit()
        await self.db.refresh(user)

        return user

    # ==========================
    # Reactivate
    # ==========================

    async def reactivate(self, user: User):
        user.is_active = True

        await self.db.commit()
        await self.db.refresh(user)

        return user