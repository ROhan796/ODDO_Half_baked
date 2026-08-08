# app/models/loyalty.py
import uuid
from sqlalchemy import (
    Column, String, DateTime, Text, Enum as SAEnum,
    ForeignKey, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
import enum


class PointsTransactionType(str, enum.Enum):
    EARNED = "earned"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    ADJUSTED = "adjusted"
    REFERRAL = "referral"


class LoyaltyPointsLedger(BaseModel):
    __tablename__ = "loyalty_points_ledger"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    transaction_type = Column(
        SAEnum(PointsTransactionType, name="points_transaction_type_enum"),
        nullable=False,
    )
    points = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    description = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)


class Referral(BaseModel):
    __tablename__ = "referrals"

    referrer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    referred_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    referral_code = Column(String(20), nullable=False)
    status = Column(
        SAEnum("pending", "completed", "expired", name="referral_status_enum"),
        default="pending",
    )
    referrer_bonus_points = Column(Integer, default=0)
    referred_bonus_points = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
