from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.repository import (
    AuthRepository,
    RefreshTokenRepository,
)
from app.modules.auth.schemas import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    CurrentUserResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import AuthService
from app.modules.roles.repository import RoleRepository
from app.modules.users.models import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ==========================
# Register
# ==========================

@router.post(
    "/register",
    response_model=UserResponse,
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    auth_repo = AuthRepository(db)
    refresh_repo = RefreshTokenRepository(db)

    service = AuthService(
        auth_repo=auth_repo,
        refresh_repo=refresh_repo,
    )

    role_repo = RoleRepository(db)

    buyer_role = await role_repo.get_by_slug(
        "buyer",
    )

    if not buyer_role:
        raise HTTPException(
            status_code=500,
            detail="Buyer role is not configured.",
        )

    try:
        return await service.register(
            request,
            role_id=buyer_role.id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ==========================
# Login
# ==========================

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(
        auth_repo=AuthRepository(db),
        refresh_repo=RefreshTokenRepository(db),
    )

    return await service.login(
        request.email,
        request.password,
    )


# ==========================
# Refresh Token
# ==========================

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(
        auth_repo=AuthRepository(db),
        refresh_repo=RefreshTokenRepository(db),
    )

    return await service.refresh(
        request.refresh_token,
    )


# ==========================
# Current User
# ==========================

@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
async def me(
    current_user: User = Depends(
        get_current_user,
    ),
):
    return current_user


# ==========================
# Logout
# ==========================

@router.post(
    "/logout",
    response_model=MessageResponse,
)
async def logout(
    request: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(
        auth_repo=AuthRepository(db),
        refresh_repo=RefreshTokenRepository(db),
    )

    return await service.logout(
        request.refresh_token,
    )


# ==========================
# Forgot Password
# ==========================

@router.post(
    "/forgot-password",
    response_model=MessageResponse,
)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(
        auth_repo=AuthRepository(db),
        refresh_repo=RefreshTokenRepository(db),
    )

    return await service.forgot_password(
        request.email,
    )


# ==========================
# Reset Password
# ==========================

@router.post(
    "/reset-password",
    response_model=MessageResponse,
)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(
        auth_repo=AuthRepository(db),
        refresh_repo=RefreshTokenRepository(db),
    )

    return await service.reset_password(
        email=request.email,
        otp=request.otp,
        password=request.password,
    )


# ==========================
# Change Password
# ==========================

@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(
        get_current_user,
    ),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(
        auth_repo=AuthRepository(db),
        refresh_repo=RefreshTokenRepository(db),
    )

    return await service.change_password(
        user=current_user,
        current_password=request.current_password,
        new_password=request.new_password,
    )