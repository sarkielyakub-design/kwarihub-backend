from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import RefreshToken


class RefreshTokenRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, token: str):
        return await self.db.scalar(
            select(RefreshToken).where(
                RefreshToken.token == token
            )
        )

    async def save(self, refresh_token: RefreshToken):
        self.db.add(refresh_token)
        await self.db.commit()

    async def revoke(self, token: str):
        refresh = await self.get(token)

        if refresh:
            refresh.is_revoked = True
            await self.db.commit()