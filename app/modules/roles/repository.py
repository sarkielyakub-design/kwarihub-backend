from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.roles.models import Role


class RoleRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # ==========================
    # Get By Name
    # ==========================

    async def get_by_name(
        self,
        name: str,
    ):
        return await self.db.scalar(
            select(Role).where(
                func.lower(Role.name) == name.lower(),
            )
        )

    # ==========================
    # Get By Slug
    # ==========================

    async def get_by_slug(
        self,
        slug: str,
    ):
        """
        Compatibility method.

        The Role model currently uses `name`,
        not `slug`.
        """

        return await self.get_by_name(
            slug,
        )

    # ==========================
    # Get By ID
    # ==========================

    async def get_by_id(
        self,
        role_id: int,
    ):
        return await self.db.scalar(
            select(Role).where(
                Role.id == role_id,
            )
        )

    # ==========================
    # Get All
    # ==========================

    async def get_all(self):
        result = await self.db.execute(
            select(Role).order_by(
                Role.name.asc(),
            )
        )

        return result.scalars().all()