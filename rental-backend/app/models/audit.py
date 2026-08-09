# app/models/audit.py
import uuid
from sqlalchemy import (
    Column, String, DateTime, Text, Enum as SAEnum,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from app.models.base import BaseModel
import enum


class AuditAction(str, enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    APPROVE = "approve"
    REJECT = "reject"


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(
        SAEnum(AuditAction, name="audit_action_enum", create_type=False),
        nullable=False,
    )
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    changes = Column(JSONB, default={})
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(36), nullable=True)
    session_id = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=True)
