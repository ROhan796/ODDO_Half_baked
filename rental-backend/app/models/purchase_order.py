# app/models/purchase_order.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, Integer
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class POStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PORequisition(BaseModel):
    __tablename__ = "po_requisitions"

    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=False)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    equipment_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    daily_rate = Column(Numeric(10, 2), nullable=True)
    rental_dates = Column(JSONB, nullable=True)
    total_amount = Column(Numeric(12, 2), nullable=True)
    department = Column(String(100), nullable=True)
    status = Column(
        SAEnum(POStatus, name="po_status_enum"),
        default=POStatus.PENDING,
    )
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)

    enterprise = relationship("Enterprise", foreign_keys=[enterprise_id])
    requestor = relationship("User", foreign_keys=[requested_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
