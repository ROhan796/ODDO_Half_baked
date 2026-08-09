# app/models/recovery.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.models.base import BaseModel
import enum


class RecoveryStatus(str, enum.Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    SUCCESSFUL = "successful"
    PARTIAL = "partial"
    FAILED = "failed"
    LEGAL = "legal"


class RecoveryCase(BaseModel):
    __tablename__ = "recovery_cases"

    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    initiated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    initiated_at = Column(DateTime(timezone=True), nullable=True)
    reason = Column(String(255), nullable=False)
    amount_outstanding = Column(Numeric(12, 2), nullable=False)
    status = Column(
        SAEnum(RecoveryStatus, name="recovery_status_enum", create_type=False),
        default=RecoveryStatus.INITIATED,
    )
    recovery_agent = Column(String(255), nullable=True)
    contact_attempts = Column(ARRAY(Text), default=[])
    last_contact_at = Column(DateTime(timezone=True), nullable=True)
    next_action_at = Column(DateTime(timezone=True), nullable=True)
    next_action_description = Column(Text, nullable=True)
    recovered_amount = Column(Numeric(12, 2), default=0)
    recovered_at = Column(DateTime(timezone=True), nullable=True)
    product_recovered = Column(Boolean, default=False)
    product_recovered_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    escalated_to_legal = Column(Boolean, default=False)
    legal_reference = Column(String(255), nullable=True)
