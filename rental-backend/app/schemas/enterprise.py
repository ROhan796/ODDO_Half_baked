# app/schemas/enterprise.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class EnterpriseCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    legal_entity_type: str = Field(..., pattern="^(private_ltd|llp|partnership|proprietorship|ngo)$")
    gst_number: Optional[str] = None
    pan: str = Field(..., min_length=10, max_length=12)
    cin: Optional[str] = None
    registered_address: dict
    office_address: Optional[dict] = None
    contact_person_name: str
    contact_person_email: str
    contact_person_phone: str


class EnterpriseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    office_address: Optional[dict] = None
    contact_person_name: Optional[str] = None
    contact_person_email: Optional[str] = None
    contact_person_phone: Optional[str] = None


class EnterpriseResponse(BaseModel):
    id: uuid.UUID
    name: str
    legal_entity_type: str
    gst_number: Optional[str] = None
    pan: str
    kyc_status: str
    trust_score: int
    credit_line_enabled: bool
    credit_limit_inr: Optional[float] = None
    credit_used_inr: float
    total_rentals: int
    total_spend: float
    created_at: datetime

    class Config:
        from_attributes = True


class EnterpriseMemberCreate(BaseModel):
    user_id: uuid.UUID
    sub_role: str = Field(..., pattern="^(admin|procurement|department_user|auditor)$")
    department: Optional[str] = None
    designation: Optional[str] = None
    spending_limit_inr: Optional[float] = None
    monthly_limit_inr: Optional[float] = None
    can_approve_rentals: bool = False


class EnterpriseMemberResponse(BaseModel):
    id: uuid.UUID
    enterprise_id: uuid.UUID
    user_id: uuid.UUID
    sub_role: str
    department: Optional[str] = None
    designation: Optional[str] = None
    spending_limit_inr: Optional[float] = None
    monthly_limit_inr: Optional[float] = None
    can_approve_rentals: bool
    invited_at: datetime
    accepted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
