# app/models/dispute.py
import uuid
from sqlalchemy import (
    Column, String, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.models.base import BaseModel
import enum


class DisputeStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class DisputeResolution(str, enum.Enum):
    FAVOR_CUSTOMER = "favor_customer"
    FAVOR_COMPANY = "favor_company"
    PARTIAL = "partial"
    WITHDRAWN = "withdrawn"


class Dispute(BaseModel):
    __tablename__ = "disputes"

    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    dispute_type = Column(
        SAEnum("late_fee", "damage", "deposit", "charge", "other", name="dispute_type_enum"),
        nullable=False,
    )
    amount_disputed = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=False)
    evidence_urls = Column(ARRAY(Text), default=[])
    status = Column(
        SAEnum(DisputeStatus, name="dispute_status_enum"),
        default=DisputeStatus.OPEN,
    )
    resolution = Column(
        SAEnum(DisputeResolution, name="dispute_resolution_enum"),
        nullable=True,
    )
    resolution_amount = Column(Numeric(12, 2), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
