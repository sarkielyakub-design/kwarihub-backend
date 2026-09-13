from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.settings.models import MarketplaceSettings


class SettingsRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get(self):
        result = await self.db.execute(
            select(MarketplaceSettings)
            .where(
                MarketplaceSettings.is_deleted == False,
            )
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        settings: MarketplaceSettings,
    ):
        self.db.add(settings)
        await self.db.commit()
        await self.db.refresh(settings)

        return settings

    async def update(
        self,
        settings: MarketplaceSettings,
    ):
        await self.db.commit()
        await self.db.refresh(settings)

        return settings