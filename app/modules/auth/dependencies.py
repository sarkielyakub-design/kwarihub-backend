from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.core.security import decode_access_token
from app.modules.users.models import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user_uuid = payload.get("sub")

    result = await db.scalar(
        select(User).where(User.uuid == user_uuid)
    )

    if not result:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return result