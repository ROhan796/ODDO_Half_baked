# app/schemas/crm.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class CRMContactCreate(BaseModel):
    contact_type: str = Field(..., pattern="^(lead|customer|partner|vendor)$")
    name: str = Field(..., min_length=2, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []


class CRMContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    status: Optional[str] = None
    lead_score: Optional[int] = None
    next_follow_up_at: Optional[datetime] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class CRMContactResponse(BaseModel):
    id: uuid.UUID
    contact_type: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: str
    lead_score: int
    lifetime_value: float
    last_contact_at: Optional[datetime] = None
    next_follow_up_at: Optional[datetime] = None
    tags: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CRMContactListResponse(BaseModel):
    items: list[CRMContactResponse]
    total: int
    page: int
    limit: int
    has_next: bool


class CRMInteractionCreate(BaseModel):
    contact_id: uuid.UUID
    interaction_type: str = Field(..., pattern="^(call|email|sms|meeting|note|whatsapp)$")
    direction: str = Field(..., pattern="^(inbound|outbound)$")
    subject: Optional[str] = None
    content: Optional[str] = None
    duration_minutes: Optional[int] = None
    outcome: Optional[str] = None
    next_action: Optional[str] = None
    next_action_at: Optional[datetime] = None


class CRMInteractionResponse(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    interaction_type: str
    direction: str
    subject: Optional[str] = None
    content: Optional[str] = None
    performed_by: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
