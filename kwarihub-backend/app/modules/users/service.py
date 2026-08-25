from fastapi import HTTPException

from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UpdateProfileRequest
from app.modules.users.models import User
from fastapi import HTTPException, status

from app.core.security import (
    verify_password,
    hash_password,
)
from app.modules.users.schemas import (
    ChangePasswordRequest,
    MessageResponse,
)

class UserService:

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def update_profile(
        self,
        current_user: User,
        data: UpdateProfileRequest,
    ):

        existing = await self.repo.get_by_username(
            data.username
        )

        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=400,
                detail="Username already exists.",
            )

        current_user.first_name = data.first_name
        current_user.last_name = data.last_name
        current_user.username = data.username
        current_user.phone = data.phone

        return await self.repo.update(current_user)
    async def change_password(
        self,
        current_user: User,
        request: ChangePasswordRequest,
    ):

        if not verify_password(
            request.current_password,
            current_user.password,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )

        if request.current_password == request.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password.",
            )

        current_user.password = hash_password(
            request.new_password
        )

        await self.repo.change_password(current_user)

        return MessageResponse(
            success=True,
            message="Password changed successfully.",
        )
    import os
import uuid

from fastapi import HTTPException, UploadFile

UPLOAD_DIR = "storage/avatars"

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_SIZE = 2 * 1024 * 1024  # 2MB

async def upload_avatar(
    self,
    current_user,
    file: UploadFile,
):

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG and WEBP images are allowed.",
        )

    contents = await file.read()

    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size cannot exceed 2MB.",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    extension = file.filename.split(".")[-1]

    filename = f"{uuid.uuid4()}.{extension}"

    path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    with open(path, "wb") as image:
        image.write(contents)

    current_user.avatar = path

    await self.repo.update_avatar(current_user)

    return {
        "success": True,
        "message": "Avatar uploaded successfully.",
        "avatar_url": path,
    }
from app.modules.users.schemas import MessageResponse


class UserService:
    ...

    async def delete_account(self, current_user):

        if current_user.is_deleted:
            raise HTTPException(
                status_code=400,
                detail="Account has already been deleted.",
            )

        await self.repo.soft_delete(current_user)

        return MessageResponse(
            success=True,
            message="Your account has been deleted successfully.",
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