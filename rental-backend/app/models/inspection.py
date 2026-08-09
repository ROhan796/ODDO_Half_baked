# app/models/inspection.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, Integer, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class InspectionType(str, enum.Enum):
    CHECKOUT = "checkout"
    RETURN = "return"


class OverallGrade(str, enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class InspectionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"


class InspectionReport(BaseModel):
    __tablename__ = "inspection_reports"

    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    inspector_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    inspection_type = Column(
        SAEnum(InspectionType, name="inspection_type_enum", create_type=False),
        nullable=False,
    )
    functional_check = Column(JSONB, default={})
    cosmetic_grade = Column(String(20), nullable=True)
    overall_grade = Column(
        SAEnum(OverallGrade, name="overall_grade_enum", create_type=False),
        nullable=True,
    )
    accessories_status = Column(JSONB, default=[])
    damage_detected = Column(Boolean, default=False)
    damage_description = Column(Text, nullable=True)
    estimated_damage_cost = Column(Numeric(10, 2), nullable=True)
    photos = Column(ARRAY(Text), default=[])
    before_photo = Column(Text, nullable=True)
    after_photo = Column(Text, nullable=True)
    status = Column(
        SAEnum(InspectionStatus, name="inspection_status_enum", create_type=False),
        default=InspectionStatus.PENDING,
    )

    rental = relationship("Rental", foreign_keys=[rental_id])
    product = relationship("Product", foreign_keys=[product_id])
    inspector = relationship("User", foreign_keys=[inspector_id])
