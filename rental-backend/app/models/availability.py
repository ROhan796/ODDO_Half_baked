# app/models/availability.py
import uuid
from sqlalchemy import (
    Column, String, DateTime, Text, Enum as SAEnum,
    ForeignKey, Date
)
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
import enum


class BlockType(str, enum.Enum):
    RENTAL = "rental"
    MAINTENANCE = "maintenance"
    RESERVATION = "reservation"
    BLACKOUT = "blackout"


class BlockStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ReservationStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class AvailabilityBlock(BaseModel):
    __tablename__ = "availability_blocks"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    block_type = Column(
        SAEnum(BlockType, name="block_type_enum", create_type=False),
        nullable=False,
    )
    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=True)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        SAEnum(BlockStatus, name="block_status_enum", create_type=False),
        default=BlockStatus.ACTIVE,
    )
    booked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)


class BlackoutDate(BaseModel):
    __tablename__ = "blackout_dates"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String(255), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)


class Reservation(BaseModel):
    __tablename__ = "reservations"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        SAEnum(ReservationStatus, name="reservation_status_enum", create_type=False),
        default=ReservationStatus.PENDING,
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    quotation_id = Column(UUID(as_uuid=True), ForeignKey("quotations.id"), nullable=True)
