# app/models/fee.py
import uuid
from sqlalchemy import (
    Column, String, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
import enum


class LateFeeStatus(str, enum.Enum):
    CALCULATED = "calculated"
    APPLIED = "applied"
    WAIVED = "waived"
    DISPUTED = "disputed"
    PARTIALLY_WAIVED = "partially_waived"


class LateFee(BaseModel):
    __tablename__ = "late_fees"

    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    days_overdue = Column(Numeric(10, 2), nullable=False)
    daily_rate = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    waived_amount = Column(Numeric(12, 2), default=0)
    status = Column(
        SAEnum(LateFeeStatus, name="late_fee_status_enum", create_type=False),
        default=LateFeeStatus.CALCULATED,
    )
    waived_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    waived_at = Column(DateTime(timezone=True), nullable=True)
    waiver_reason = Column(Text, nullable=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id"), nullable=True)
    calculated_at = Column(DateTime(timezone=True), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)
