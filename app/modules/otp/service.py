from random import randint

from fastapi import HTTPException, status

from app.modules.otp.models import OTP
from app.modules.otp.repository import OTPRepository
from app.modules.users.repository import UserRepository
from app.tasks.email import (
    send_reset_password_email,
    send_verify_email,
    send_welcome_email,
)


class OTPService:

    def __init__(
        self,
        repo: OTPRepository,
        user_repo: UserRepository,
    ):
        self.repo = repo
        self.user_repo = user_repo

    # ==========================
    # Generate OTP
    # ==========================

    async def generate(
        self,
        user_id: int,
        purpose: str = "email_verification",
    ):
        user = await self.user_repo.get_by_id(
            user_id,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        # Remove previous active OTPs
        await self.repo.delete_user_codes(
            user_id=user.id,
            purpose=purpose,
        )

        code = str(
            randint(
                100000,
                999999,
            )
        )

        otp = OTP(
            user_id=user.id,
            code=code,
            purpose=purpose,
        )

        await self.repo.create(otp)

        # ==========================
        # Email Verification
        # ==========================

        if purpose == "email_verification":

            send_verify_email.delay(
                user.email,
                user.first_name,
                code,
            )

        # ==========================
        # Password Reset
        # ==========================

        elif purpose == "password_reset":

            send_reset_password_email.delay(
                user.email,
                user.first_name,
                code,
            )

        return {
            "success": True,
            "message": "OTP sent successfully.",
        }

    # ==========================
    # Verify OTP
    # ==========================

    async def verify(
        self,
        user_id: int,
        code: str,
        purpose: str = "email_verification",
        update_user_verification: bool = True,
    ):
        otp = await self.repo.get_valid_code(
            user_id=user_id,
            purpose=purpose,
            code=code,
        )

        if not otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP.",
            )

        user = await self.user_repo.get_by_id(
            user_id,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        # Mark OTP as used
        await self.repo.mark_used(
            otp,
        )

        # Only email verification should
        # change the verification status.
        if (
            purpose == "email_verification"
            and update_user_verification
            and not user.is_verified
        ):
            user.is_verified = True

            await self.user_repo.update(
                user,
            )

            # Welcome email only after
            # successful email verification.
            send_welcome_email.delay(
                user.email,
                user.first_name,
            )

        return {
            "success": True,
            "message": (
                "Email verified successfully."
                if purpose == "email_verification"
                else "OTP verified successfully."
            ),
        }

    # ==========================
    # Resend Verification OTP
    # ==========================

    async def resend(
        self,
        user_id: int,
    ):
        user = await self.user_repo.get_by_id(
            user_id,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified.",
            )

        return await self.generate(
            user_id=user.id,
            purpose="email_verification",
        )