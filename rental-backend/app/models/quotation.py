# app/models/quotation.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, Integer
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class QuotationStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED = "converted"


class Quotation(BaseModel):
    __tablename__ = "quotations"

    quote_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=True)
    status = Column(
        SAEnum(QuotationStatus, name="quotation_status_enum"),
        default=QuotationStatus.DRAFT,
    )
    items = Column(JSONB, nullable=False, default=[])
    subtotal = Column(Numeric(12, 2), nullable=False)
    tax_amount = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    deposit_amount = Column(Numeric(12, 2), default=0)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    converted_to_rental = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    customer = relationship("User", foreign_keys=[customer_id])
    template = relationship("QuotationTemplate", back_populates="quotations")


class QuotationTemplate(BaseModel):
    __tablename__ = "quotation_templates"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_data = Column(JSONB, nullable=False, default={})
    is_default = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    quotations = relationship("Quotation", back_populates="template")
