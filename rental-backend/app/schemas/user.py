# app/schemas/user.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date
import uuid


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(..., pattern="^[6-9]\\d{9}$")
    password: Optional[str] = None
    user_type: str = Field("personal", pattern="^(personal|enterprise|enterprise_sub)$")
    role: str = Field("portal_user", pattern="^(super_admin|ops_admin|field_agent|portal_user)$")
    dob: Optional[date] = None
    enterprise_id: Optional[uuid.UUID] = None


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern="^[6-9]\\d{9}$")
    dob: Optional[date] = None
    profile_photo_url: Optional[str] = None
    notification_preferences: Optional[dict] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    user_type: str
    role: str
    phone: str
    email: str
    name: str
    dob: Optional[date] = None
    profile_photo_url: Optional[str] = None
    kyc_status: str
    trust_score: int
    trust_tier: str
    blacklisted: bool
    points_balance: int
    lifetime_rentals: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    limit: int
    has_next: bool
