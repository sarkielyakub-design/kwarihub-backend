from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str
    avatar: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    first_name: str
    last_name: str
    username: str
    phone: str


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class AvatarResponse(BaseModel):
    success: bool
    message: str
    avatar_url: str


class MessageResponse(BaseModel):
    success: bool
    message: str