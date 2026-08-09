# app/models/software_service.py
import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean, Date, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, Integer, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class LicenseType(str, enum.Enum):
    SAAS_SUBSCRIPTION = "saas_subscription"
    NODE_LOCKED = "node_locked"
    FLOATING = "floating"
    CLOUD_CREDIT = "cloud_credit"
    API_QUOTA = "api_quota"


class SoftwareDeliveryMethod(str, enum.Enum):
    EMAIL_LICENSE_KEY = "email_license_key"
    CLOUD_ACCESS = "cloud_access"
    API_KEY = "api_key"
    DOWNLOAD_LINK = "download_link"


class SoftwareServiceStatus(str, enum.Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    DEPRECATED = "deprecated"
    INACTIVE = "inactive"


class SoftwareRentalStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class SoftwareService(BaseModel):
    __tablename__ = "software_services"

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)

    vendor = Column(String(255), nullable=True)
    version = Column(String(50), nullable=True)
    license_type = Column(
        SAEnum(LicenseType, name="license_type_enum"),
        nullable=False,
    )
    delivery_method = Column(
        SAEnum(SoftwareDeliveryMethod, name="software_delivery_method_enum"),
        nullable=False,
    )

    hourly_rate = Column(Numeric(10, 2), nullable=True)
    daily_rate = Column(Numeric(10, 2), nullable=True)
    weekly_rate = Column(Numeric(10, 2), nullable=True)
    monthly_rate = Column(Numeric(10, 2), nullable=True)
    annual_rate = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), default="INR")

    max_concurrent_users = Column(Integer, default=1)
    max_seats = Column(Integer, nullable=True)
    requires_vpn = Column(Boolean, default=False)
    ip_whitelist = Column(ARRAY(Text), default=[])

    system_requirements = Column(Text, nullable=True)
    api_endpoint = Column(Text, nullable=True)
    documentation_url = Column(Text, nullable=True)
    support_email = Column(String(255), nullable=True)

    metadata_ = Column("metadata", JSONB, default={})
    tags = Column(ARRAY(Text), default=[])
    images = Column(ARRAY(Text), default=[])
    thumbnail_url = Column(Text, nullable=True)

    status = Column(
        SAEnum(SoftwareServiceStatus, name="software_service_status_enum"),
        default=SoftwareServiceStatus.AVAILABLE,
    )
    is_featured = Column(Boolean, default=False)

    # Relationships
    category = relationship("Category", foreign_keys=[category_id])
    software_rentals = relationship("SoftwareRental", back_populates="software_service")


class SoftwareRental(BaseModel):
    __tablename__ = "software_rentals"

    rental_number = Column(String(20), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    software_service_id = Column(
        UUID(as_uuid=True), ForeignKey("software_services.id"), nullable=False
    )

    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    actual_access_revoked_at = Column(DateTime(timezone=True), nullable=True)

    license_key = Column(Text, nullable=True)
    license_server_url = Column(Text, nullable=True)
    api_key_hash = Column(String(255), nullable=True)
    access_credentials = Column(JSONB, nullable=True)

    rental_fee = Column(Numeric(12, 2), nullable=False)
    security_deposit_amount = Column(Numeric(12, 2), default=0)
    currency = Column(String(3), default="INR")

    usage_metric = Column(String(50), nullable=True)
    usage_limit = Column(Numeric(12, 2), nullable=True)
    usage_current = Column(Numeric(12, 2), default=0)

    status = Column(
        SAEnum(SoftwareRentalStatus, name="software_rental_status_enum"),
        default=SoftwareRentalStatus.PENDING,
    )

    provisioned_at = Column(DateTime(timezone=True), nullable=True)
    access_granted_at = Column(DateTime(timezone=True), nullable=True)
    access_revoked_at = Column(DateTime(timezone=True), nullable=True)

    quotation_id = Column(UUID(as_uuid=True), ForeignKey("quotations.id"), nullable=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    customer = relationship("User", foreign_keys=[customer_id])
    software_service = relationship("SoftwareService", back_populates="software_rentals")
    created_by_user = relationship("User", foreign_keys=[created_by])


class SoftwareUsageLog(BaseModel):
    __tablename__ = "software_usage_logs"

    software_rental_id = Column(
        UUID(as_uuid=True), ForeignKey("software_rentals.id"), nullable=False
    )
    metric_type = Column(String(50), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False)
    metadata_ = Column("metadata", JSONB, default={})

    # Relationships
    software_rental = relationship("SoftwareRental", foreign_keys=[software_rental_id])
