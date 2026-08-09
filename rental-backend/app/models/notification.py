# app/models/notification.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, JSON, Integer
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import BaseModel
import enum


class NotificationType(str, enum.Enum):
    RENTAL = "rental"
    PAYMENT = "payment"
    REMINDER = "reminder"
    SYSTEM = "system"
    MARKETING = "marketing"


class NotificationChannel(str, enum.Enum):
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(
        SAEnum(NotificationType, name="notification_type_enum", create_type=False),
        nullable=False,
    )
    channel = Column(
        SAEnum(NotificationChannel, name="notification_channel_enum", create_type=False),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSONB, default={})
    status = Column(
        SAEnum(NotificationStatus, name="notification_status_enum", create_type=False),
        default=NotificationStatus.PENDING,
    )
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    reference_type = Column(String(50), nullable=True)


class NotificationTemplate(BaseModel):
    __tablename__ = "notification_templates"

    name = Column(String(255), unique=True, nullable=False)
    type = Column(
        SAEnum(NotificationType, name="notification_template_type_enum", create_type=False),
        nullable=False,
    )
    channel = Column(
        SAEnum(NotificationChannel, name="notification_template_channel_enum", create_type=False),
        nullable=False,
    )
    subject = Column(String(255), nullable=True)
    body_template = Column(Text, nullable=False)
    variables = Column(JSONB, default=[])
    is_active = Column(Boolean, default=True)
