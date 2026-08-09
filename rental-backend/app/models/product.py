# app/models/product.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, Date, Text, Enum as SAEnum,
    ForeignKey, Numeric, SmallInteger, Integer, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class ProductStatus(str, enum.Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    IN_REPAIR = "in_repair"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class LateFeeMode(str, enum.Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Category(BaseModel):
    __tablename__ = "categories"

    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    icon_url = Column(Text, nullable=True)
    deposit_percentage_override = Column(Numeric(5, 2), nullable=True)
    late_fee_rate_override = Column(Numeric(10, 2), nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    parent = relationship("Category", remote_side="Category.id", backref="subcategories")
    products = relationship("Product", back_populates="category")


class Product(BaseModel):
    __tablename__ = "products"

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    serial_number = Column(String(100), unique=True, nullable=True)
    qr_code = Column(String(255), unique=True, nullable=True)
    rfid_tag = Column(String(100), nullable=True)
    barcode = Column(String(100), nullable=True)
    sku = Column(String(100), unique=True, nullable=True)
    status = Column(
        SAEnum(ProductStatus, name="product_status_enum", create_type=False),
        default=ProductStatus.AVAILABLE,
    )
    current_holder_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    current_rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=True)
    condition_rating = Column(SmallInteger, default=5)
    condition_notes = Column(Text, nullable=True)
    purchase_date = Column(Date, nullable=True)
    purchase_price = Column(Numeric(12, 2), nullable=True)
    current_value = Column(Numeric(12, 2), nullable=True)
    depreciation_rate = Column(Numeric(5, 2), default=0)
    insurance_expiry = Column(Date, nullable=True)
    warranty_expiry = Column(Date, nullable=True)
    location = Column(String(255), nullable=True)
    is_insured = Column(Boolean, default=False)
    daily_rate = Column(Numeric(10, 2), nullable=True)
    deposit_percentage = Column(Numeric(5, 2), default=30.00)
    late_fee_rate = Column(Numeric(10, 2), nullable=True)
    late_fee_mode = Column(
        SAEnum(LateFeeMode, name="late_fee_mode_enum", create_type=False),
        default=LateFeeMode.DAILY,
    )
    grace_period_minutes = Column(Integer, default=30)
    max_late_fee_multiplier = Column(Numeric(3, 1), default=2.0)
    min_rental_duration = Column(Integer, default=1)
    max_rental_duration = Column(Integer, nullable=True)
    images = Column(ARRAY(Text), default=[])
    thumbnail_url = Column(Text, nullable=True)
    tags = Column(ARRAY(Text), default=[])
    metadata_ = Column("metadata", JSONB, default={})
    total_rentals = Column(Integer, default=0)
    total_revenue = Column(Numeric(14, 2), default=0)
    total_damage_reports = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    accessories = relationship("Accessory", back_populates="product", cascade="all, delete-orphan")


class ProductVariant(BaseModel):
    __tablename__ = "product_variants"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    attribute = Column(String(50), nullable=False)
    value = Column(String(100), nullable=False)
    sku = Column(String(100), unique=True, nullable=True)
    additional_price_inr = Column(Numeric(10, 2), default=0)
    is_default = Column(Boolean, default=False)

    product = relationship("Product", back_populates="variants")


class Accessory(BaseModel):
    __tablename__ = "accessories"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    item_code = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    replacement_cost_inr = Column(Numeric(10, 2), nullable=False)
    is_required = Column(Boolean, default=True)
    condition_rating = Column(SmallInteger, default=5)
    image_url = Column(Text, nullable=True)

    product = relationship("Product", back_populates="accessories")
