# app/models/blacklist.py
import uuid
from sqlalchemy import (
    Column, String, DateTime, Text, Enum as SAEnum,
    ForeignKey, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
import enum


class BlacklistReason(str, enum.Enum):
    PAYMENT_FRAUD = "payment_fraud"
    IDENTITY_FRAUD = "identity_fraud"
    THEFT = "theft"
    DAMAGE = "damage"
    NON_PAYMENT = "non_payment"
    OTHER = "other"


class Blacklist(BaseModel):
    __tablename__ = "blacklists"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason = Column(
        SAEnum(BlacklistReason, name="blacklist_reason_enum"),
        nullable=False,
    )
    description = Column(Text, nullable=True)
    evidence_urls = Column(Text, nullable=True)
    added_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    added_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_permanent = Column(Boolean, default=False)
    removed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    removed_at = Column(DateTime(timezone=True), nullable=True)
    removal_reason = Column(Text, nullable=True)
