from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.schemas import (
    AvatarResponse,
    ChangePasswordRequest,
    MessageResponse,
)
from fastapi import UploadFile, File
from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    UserProfileResponse,
    UpdateProfileRequest,
)
from app.modules.users.service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/profile",
    response_model=UserProfileResponse,
)
async def profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.put(
    "/profile",
    response_model=UserProfileResponse,
)
async def update_profile(
    request: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    service = UserService(repo)

    return await service.update_profile(
        current_user,
        request,
    )
@router.post(
    "/change-password",
    response_model=MessageResponse,
)
async def change_password(
    request: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    service = UserService(repo)

    return await service.change_password(
        current_user,
        request,
    )
@router.post(
    "/avatar",
    response_model=AvatarResponse,
)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    service = UserService(repo)

    return await service.upload_avatar(
        current_user,
        file,
    )
@router.delete(
    "/account",
    response_model=MessageResponse,
)
async def delete_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    service = UserService(repo)

    return await service.delete_account(current_user)
from fastapi import HTTPException, status
from app.modules.users.schemas import MessageResponse


async def deactivate_account(
    self,
    current_user,
):

    if current_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deleted accounts cannot be deactivated.",
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already deactivated.",
        )

    await self.repo.deactivate(current_user)

    return MessageResponse(
        success=True,
        message="Your account has been deactivated.",
    )


async def reactivate_account(
    self,
    user,
):

    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deleted accounts cannot be reactivated.",
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already active.",
        )

    await self.repo.reactivate(user)

    return MessageResponse(
        success=True,
        message="Account reactivated successfully.",
    )
from fastapi import HTTPException, status
from app.modules.users.schemas import MessageResponse


async def deactivate_account(
    self,
    current_user,
):

    if current_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deleted accounts cannot be deactivated.",
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already deactivated.",
        )

    await self.repo.deactivate(current_user)

    return MessageResponse(
        success=True,
        message="Your account has been deactivated.",
    )


async def reactivate_account(
    self,
    user,
):

    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deleted accounts cannot be reactivated.",
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already active.",
        )

    await self.repo.reactivate(user)

    return MessageResponse(
        success=True,
        message="Account reactivated successfully.",
    )