from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str
class LogoutRequest(BaseModel):
    refresh_token: str    
from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(
        min_length=6,
        max_length=6,
    )
    password: str = Field(
        min_length=8,
    )


class MessageResponse(BaseModel):
    success: bool
    message: str    
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(
        min_length=8,
    )

    new_password: str = Field(
        min_length=8,
    )
class ChangePasswordResponse(BaseModel):
    success: bool
    message: str        