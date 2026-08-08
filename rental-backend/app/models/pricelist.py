# app/models/pricelist.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text,
    ForeignKey, Numeric, Integer
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Pricelist(BaseModel):
    __tablename__ = "pricelists"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    items = relationship("PricelistItem", back_populates="pricelist", cascade="all, delete-orphan")


class PricelistItem(BaseModel):
    __tablename__ = "pricelist_items"

    pricelist_id = Column(UUID(as_uuid=True), ForeignKey("pricelists.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    rental_type = Column(String(20), nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="INR")
    min_duration = Column(Integer, default=1)
    max_duration = Column(Integer, nullable=True)
    deposit_percentage = Column(Numeric(5, 2), nullable=True)
    late_fee_rate = Column(Numeric(10, 2), nullable=True)
    metadata_ = Column("metadata", JSONB, default={})

    pricelist = relationship("Pricelist", back_populates="items")
