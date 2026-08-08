# app/schemas/notification.py
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
import uuid


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    channel: str
    title: str
    message: str
    data: dict = {}
    status: str
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int


class NotificationTemplateCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    type: str = Field(..., pattern="^(rental|payment|reminder|system|marketing)$")
    channel: str = Field(..., pattern="^(sms|email|push|in_app)$")
    subject: Optional[str] = None
    body_template: str
    variables: list[str] = []


class NotificationTemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    channel: str
    subject: Optional[str] = None
    body_template: str
    variables: list[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
