from pydantic import BaseModel, Field


# ==========================
# Verify OTP
# ==========================

class VerifyOTPRequest(BaseModel):
    email: str
    code: str = Field(
        min_length=6,
        max_length=6,
    )


# ==========================
# Resend OTP
# ==========================

class ResendOTPRequest(BaseModel):
    email: str


# ==========================
# OTP Response
# ==========================

class OTPResponse(BaseModel):
    success: bool
    message: str