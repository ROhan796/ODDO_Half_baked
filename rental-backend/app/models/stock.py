# app/models/stock.py
import uuid
from sqlalchemy import (
    Column, String, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, Integer, Boolean
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import BaseModel
import enum


class MovementType(str, enum.Enum):
    IN = "in"
    OUT = "out"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    RETURN = "return"


class StockLocation(BaseModel):
    __tablename__ = "stock_locations"

    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    contact_person = Column(String(255), nullable=True)
    contact_phone = Column(String(15), nullable=True)
    is_active = Column(Boolean, default=True)
    is_warehouse = Column(Boolean, default=False)
    capacity = Column(Integer, nullable=True)


class StockMovement(BaseModel):
    __tablename__ = "stock_movements"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    from_location_id = Column(UUID(as_uuid=True), ForeignKey("stock_locations.id"), nullable=True)
    to_location_id = Column(UUID(as_uuid=True), ForeignKey("stock_locations.id"), nullable=True)
    movement_type = Column(
        SAEnum(MovementType, name="stock_movement_type_enum"),
        nullable=False,
    )
    quantity = Column(Integer, nullable=False)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    notes = Column(Text, nullable=True)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)


class StockLevel(BaseModel):
    __tablename__ = "stock_levels"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("stock_locations.id"), nullable=False)
    quantity = Column(Integer, default=0)
    reserved = Column(Integer, default=0)
    available = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    max_stock = Column(Integer, nullable=True)
    last_counted_at = Column(DateTime(timezone=True), nullable=True)
    last_received_at = Column(DateTime(timezone=True), nullable=True)
