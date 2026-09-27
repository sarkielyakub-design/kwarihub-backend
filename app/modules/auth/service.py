from datetime import datetime, timedelta

from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.modules.auth.models import RefreshToken
from app.modules.auth.repository import (
    AuthRepository,
    RefreshTokenRepository,
)
from app.modules.auth.schemas import RegisterRequest
from app.modules.otp.repository import OTPRepository
from app.modules.otp.service import OTPService
from app.modules.users.models import User
from app.modules.users.repository import UserRepository


class AuthService:

    def __init__(
        self,
        auth_repo: AuthRepository,
        refresh_repo: RefreshTokenRepository,
    ):
        self.repo = auth_repo
        self.refresh_repo = refresh_repo

    # ==========================
    # Register
    # ==========================

    async def register(
        self,
        data: RegisterRequest,
        role_id: int,
    ):
        if await self.repo.get_by_email(data.email):
            raise ValueError("Email already exists")

        if await self.repo.get_by_username(data.username):
            raise ValueError("Username already exists")

        if await self.repo.get_by_phone(data.phone):
            raise ValueError("Phone number already exists")

        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role_id=role_id,
            is_verified=False,
        )

        user = await self.repo.create(user)

        otp_service = OTPService(
            repo=OTPRepository(self.repo.db),
            user_repo=UserRepository(self.repo.db),
        )

        await otp_service.generate(
            user_id=user.id,
            purpose="email_verification",
        )

        return user

    # ==========================
    # Login
    # ==========================

    async def login(
        self,
        email: str,
        password: str,
    ):
        user = await self.repo.get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email before logging in.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been deactivated.",
            )

        access_token = create_access_token(
            subject=str(user.uuid),
        )

        refresh_token = create_refresh_token(
            subject=str(user.uuid),
        )

        refresh = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=30),
            device_name="Unknown Device",
            ip_address=None,
        )

        await self.refresh_repo.create(refresh)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }

    # ==========================
    # Refresh Token
    # ==========================

    async def refresh(
        self,
        refresh_token: str,
    ):
        payload = decode_access_token(
            refresh_token,
        )

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        access_token = create_access_token(
            subject=payload["sub"],
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    # ==========================
    # Logout
    # ==========================

    async def logout(
        self,
        refresh_token: str,
    ):
        token = await self.refresh_repo.get_by_token(
            refresh_token,
        )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refresh token not found",
            )

        await self.refresh_repo.revoke(token)

        return {
            "success": True,
            "message": "Logged out successfully",
        }

    # ==========================
    # Forgot Password
    # ==========================

    async def forgot_password(
        self,
        email: str,
    ):
        user = await self.repo.get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        otp_service = OTPService(
            repo=OTPRepository(self.repo.db),
            user_repo=UserRepository(self.repo.db),
        )

        await otp_service.generate(
            user_id=user.id,
            purpose="password_reset",
        )

        return {
            "success": True,
            "message": "Password reset code has been sent to your email.",
        }

    # ==========================
    # Reset Password
    # ==========================

    async def reset_password(
        self,
        email: str,
        otp: str,
        password: str,
    ):
        user = await self.repo.get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        otp_service = OTPService(
            repo=OTPRepository(self.repo.db),
            user_repo=UserRepository(self.repo.db),
        )

        # Verify password reset OTP.
        # IMPORTANT:
        # This should only validate and consume the OTP.
        await otp_service.verify(
            user_id=user.id,
            code=otp,
            purpose="password_reset",
            update_user_verification=False,
        )

        user.password_hash = hash_password(
            password,
        )

        await UserRepository(
            self.repo.db,
        ).change_password(user)

        return {
            "success": True,
            "message": "Password reset successfully.",
        }

    # ==========================
    # Change Password
    # ==========================

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ):
        if not verify_password(
            current_password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )

        if verify_password(
            new_password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from your current password.",
            )

        user.password_hash = hash_password(
            new_password,
        )

        await UserRepository(
            self.repo.db,
        ).change_password(user)

        return {
            "success": True,
            "message": "Password changed successfully.",
        }