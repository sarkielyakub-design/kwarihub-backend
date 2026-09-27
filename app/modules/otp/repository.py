from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.otp.models import OTP


class OTPRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        otp: OTP,
    ):
        self.db.add(otp)
        await self.db.commit()
        await self.db.refresh(otp)
        return otp

    async def get_valid_code(
        self,
        user_id: int,
        purpose: str,
        code: str,
    ):
        result = await self.db.execute(
            select(OTP).where(
                OTP.user_id == user_id,
                OTP.purpose == purpose,
                OTP.code == code,
                OTP.is_used == False,
                OTP.expires_at > datetime.utcnow(),
            )
        )

        return result.scalar_one_or_none()

    async def get_latest(
        self,
        user_id: int,
        purpose: str,
    ):
        result = await self.db.execute(
            select(OTP)
            .where(
                OTP.user_id == user_id,
                OTP.purpose == purpose,
                OTP.is_used == False,
            )
            .order_by(
                OTP.id.desc(),
            )
        )

        return result.scalar_one_or_none()

    async def mark_used(
        self,
        otp: OTP,
    ):
        otp.is_used = True

        await self.db.commit()
        await self.db.refresh(otp)

        return otp

    async def delete_expired(self):
        await self.db.execute(
            delete(OTP).where(
                OTP.expires_at < datetime.utcnow(),
            )
        )

        await self.db.commit()

    async def delete_user_codes(
        self,
        user_id: int,
        purpose: str,
    ):
        await self.db.execute(
            delete(OTP).where(
                OTP.user_id == user_id,
                OTP.purpose == purpose,
            )
        )

        await self.db.commit()