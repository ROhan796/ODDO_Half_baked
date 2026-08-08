# app/schemas/auth.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Phone number or email")
    password: Optional[str] = None
    device_fingerprint: str = Field(..., description="Unique device identifier")


class OTPRequest(BaseModel):
    identifier: str = Field(..., description="Phone number or email")
    channel: str = Field("sms", pattern="^(sms|email)$")


class OTPVerifyRequest(BaseModel):
    identifier: str
    code: str = Field(..., min_length=6, max_length=6)
    purpose: str = Field("login", pattern="^(login|register|kyc|transaction|extension)$")


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(..., pattern="^[6-9]\\d{9}$")
    password: Optional[str] = None
    user_type: str = Field("personal", pattern="^(personal|enterprise|group)$")
    enterprise_id: Optional[uuid.UUID] = None
    referral_code: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    device_fingerprint: str


class LogoutRequest(BaseModel):
    refresh_token: str
    device_fingerprint: str


class PasswordResetRequest(BaseModel):
    identifier: str = Field(..., description="Phone number or email")


class PasswordResetConfirm(BaseModel):
    identifier: str
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)
