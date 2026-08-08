# app/models/custody.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, SmallInteger
)
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
import enum


class CustodyEventType(str, enum.Enum):
    CHECKOUT = "checkout"
    CHECKIN = "checkin"
    TRANSFER = "transfer"
    INSPECTION = "inspection"


class CustodyEvent(BaseModel):
    __tablename__ = "custody_events"

    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    event_type = Column(
        SAEnum(CustodyEventType, name="custody_event_type_enum"),
        nullable=False,
    )
    from_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    condition_rating = Column(SmallInteger, nullable=True)
    condition_notes = Column(Text, nullable=True)
    photos = Column(Text, nullable=True)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)


class AccessoryCheck(BaseModel):
    __tablename__ = "accessory_checks"

    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=False)
    accessory_id = Column(UUID(as_uuid=True), ForeignKey("accessories.id"), nullable=False)
    checked_out = Column(Boolean, nullable=False)
    returned = Column(Boolean, nullable=True)
    condition_at_checkout = Column(SmallInteger, nullable=True)
    condition_at_return = Column(SmallInteger, nullable=True)
    missing = Column(Boolean, default=False)
    damage_charged = Column(Numeric(10, 2), nullable=True)
    notes = Column(Text, nullable=True)
