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
    ) -> Role | None:
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
    ) -> Role | None:
        return await self.db.scalar(
            select(Role).where(
                func.lower(Role.slug) == slug.lower(),
            )
        )

    # ==========================
    # Get By ID
    # ==========================

    async def get_by_id(
        self,
        role_id: int,
    ) -> Role | None:
        return await self.db.scalar(
            select(Role).where(
                Role.id == role_id,
            )
        )

    # ==========================
    # Get All
    # ==========================

    async def get_all(self) -> list[Role]:
        result = await self.db.execute(
            select(Role).order_by(
                Role.name.asc(),
            )
        )

        return list(result.scalars().all())