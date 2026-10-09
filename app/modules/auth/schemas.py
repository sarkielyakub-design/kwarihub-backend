from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


# ==========================================================
# Register
# ==========================================================

class RegisterRequest(BaseModel):
    first_name: str = Field(
        min_length=2,
        max_length=100,
    )

    last_name: str = Field(
        min_length=2,
        max_length=100,
    )

    username: str = Field(
        min_length=3,
        max_length=50,
    )

    email: EmailStr

    phone: str = Field(
        min_length=7,
        max_length=20,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    # ------------------------------------------------------
    # Account type
    #
    # buyer  -> Buyer role
    # vendor -> Buyer + Vendor roles
    # ------------------------------------------------------

    account_type: Literal[
        "buyer",
        "vendor",
    ] = "buyer"


# ==========================================================
# Login
# ==========================================================

class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


# ==========================================================
# Refresh Token
# ==========================================================

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        min_length=1,
    )


# ==========================================================
# Token Response
# ==========================================================

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ==========================================================
# User Response
# ==========================================================

class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    uuid: str
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str


# ==========================================================
# Current User Response
# ==========================================================

class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    uuid: str
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str


# ==========================================================
# Logout
# ==========================================================

class LogoutRequest(BaseModel):
    refresh_token: str = Field(
        min_length=1,
    )


# ==========================================================
# Forgot Password
# ==========================================================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# ==========================================================
# Reset Password
# ==========================================================

class ResetPasswordRequest(BaseModel):
    email: EmailStr

    otp: str = Field(
        min_length=6,
        max_length=6,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


# ==========================================================
# Generic Message Response
# ==========================================================

class MessageResponse(BaseModel):
    success: bool
    message: str


# ==========================================================
# Change Password
# ==========================================================

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(
        min_length=8,
        max_length=128,
    )

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )


# ==========================================================
# Change Password Response
# ==========================================================

class ChangePasswordResponse(BaseModel):
    success: bool
    message: str