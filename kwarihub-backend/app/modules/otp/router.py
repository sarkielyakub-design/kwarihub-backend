from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.otp.repository import OTPRepository
from app.modules.otp.schemas import (
    OTPResponse,
    ResendOTPRequest,
    VerifyOTPRequest,
)
from app.modules.otp.service import OTPService
from app.modules.users.repository import UserRepository


router = APIRouter(
    prefix="/otp",
    tags=["OTP"],
)


# ==========================
# Verify OTP
# ==========================

@router.post(
    "/verify",
    response_model=OTPResponse,
)
async def verify(
    request: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)

    user = await user_repo.get_by_email(
        request.email,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    service = OTPService(
        repo=OTPRepository(db),
        user_repo=user_repo,
    )

    return await service.verify(
        user_id=user.id,
        code=request.code,
        purpose="email_verification",
        update_user_verification=True,
    )


# ==========================
# Resend Verification OTP
# ==========================

@router.post(
    "/resend",
    response_model=OTPResponse,
)
async def resend(
    request: ResendOTPRequest,
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)

    user = await user_repo.get_by_email(
        request.email,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    service = OTPService(
        repo=OTPRepository(db),
        user_repo=user_repo,
    )

    return await service.resend(
        user.id,
    )