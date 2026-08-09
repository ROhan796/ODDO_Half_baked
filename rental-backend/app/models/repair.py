# app/models/repair.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, Integer
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.models.base import BaseModel
import enum


class RepairStatus(str, enum.Enum):
    REPORTED = "reported"
    ASSESSED = "assessed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    WRITE_OFF = "write_off"


class RepairCase(BaseModel):
    __tablename__ = "repair_cases"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=True)
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reported_at = Column(DateTime(timezone=True), nullable=True)
    damage_description = Column(Text, nullable=False)
    damage_photos = Column(ARRAY(Text), default=[])
    estimated_cost = Column(Numeric(12, 2), nullable=True)
    actual_cost = Column(Numeric(12, 2), nullable=True)
    status = Column(
        SAEnum(RepairStatus, name="repair_status_enum"),
        default=RepairStatus.REPORTED,
    )
    assigned_to = Column(String(255), nullable=True)
    vendor_name = Column(String(255), nullable=True)
    vendor_reference = Column(String(255), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    charged_to_customer = Column(Boolean, default=False)
    customer_charge_amount = Column(Numeric(12, 2), nullable=True)
