# app/models/deposit.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class DepositStatus(str, enum.Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    SETTLED = "settled"
    PARTIALLY_DEDUCTED = "partially_deducted"
    FORFEITED = "forfeited"
    REFUNDED = "refunded"


class SecurityDeposit(BaseModel):
    __tablename__ = "security_deposits"

    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(
        SAEnum(DepositStatus, name="deposit_status_enum"),
        default=DepositStatus.PENDING,
    )
    authorization_code = Column(String(255), nullable=True)
    captured_at = Column(DateTime(timezone=True), nullable=True)
    settled_at = Column(DateTime(timezone=True), nullable=True)
    refund_amount = Column(Numeric(12, 2), nullable=True)
    refund_at = Column(DateTime(timezone=True), nullable=True)
    refund_reference = Column(String(255), nullable=True)
    deductions = relationship("DepositDeduction", back_populates="deposit", cascade="all, delete-orphan")


class DepositDeduction(BaseModel):
    __tablename__ = "deposit_deductions"

    deposit_id = Column(UUID(as_uuid=True), ForeignKey("security_deposits.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    reason = Column(String(255), nullable=False)
    deduction_type = Column(
        SAEnum("late_fee", "damage", "missing_item", "other", name="deduction_type_enum"),
        nullable=False,
    )
    documented_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    documentation_url = Column(Text, nullable=True)
    customer_notified = Column(Boolean, default=False)
    customer_disputed = Column(Boolean, default=False)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id"), nullable=True)

    deposit = relationship("SecurityDeposit", back_populates="deductions")
