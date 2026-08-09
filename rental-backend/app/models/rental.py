# app/models/rental.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, Date, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class RentalStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class RentalType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Rental(BaseModel):
    __tablename__ = "rentals"

    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quotation_id = Column(UUID(as_uuid=True), ForeignKey("quotations.id"), nullable=True)
    order_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(
        SAEnum(RentalStatus, name="rental_status_enum"),
        default=RentalStatus.PENDING,
    )
    rental_type = Column(
        SAEnum(RentalType, name="rental_type_enum"),
        nullable=False,
    )
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    actual_return_date = Column(Date, nullable=True)
    daily_rate = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    deposit_amount = Column(Numeric(12, 2), default=0)
    late_fees = Column(Numeric(12, 2), default=0)
    damage_charges = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    insurance_selected = Column(Boolean, default=False)
    insurance_amount = Column(Numeric(10, 2), default=0)
    delivery_address = Column(Text, nullable=True)
    special_requirements = Column(Text, nullable=True)
    confirmed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    returned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    returned_at = Column(DateTime(timezone=True), nullable=True)
    condition_at_checkout = Column(Text, nullable=True)
    condition_at_return = Column(Text, nullable=True)
    checkout_photos = Column(Text, nullable=True)
    return_photos = Column(Text, nullable=True)

    # Relationships
    customer = relationship("User", foreign_keys=[customer_id])
    product = relationship("Product", foreign_keys=[product_id])
    extensions = relationship("RentalExtension", back_populates="rental", cascade="all, delete-orphan")


class RentalExtension(BaseModel):
    __tablename__ = "rental_extensions"

    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id", ondelete="CASCADE"), nullable=False)
    original_end_date = Column(Date, nullable=False)
    new_end_date = Column(Date, nullable=False)
    extension_days = Column(Integer, nullable=False)
    additional_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(
        SAEnum("pending", "approved", "rejected", name="extension_status_enum"),
        default="pending",
    )
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    rental = relationship("Rental", back_populates="extensions")
