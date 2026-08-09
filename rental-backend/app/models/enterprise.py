# app/models/enterprise.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, Integer
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class LegalEntityType(str, enum.Enum):
    PRIVATE_LTD = "private_ltd"
    LLP = "llp"
    PARTNERSHIP = "partnership"
    PROPRIETORSHIP = "proprietorship"
    NGO = "ngo"


class EnterpriseSubRole(str, enum.Enum):
    ADMIN = "admin"
    PROCUREMENT = "procurement"
    DEPARTMENT_USER = "department_user"
    AUDITOR = "auditor"


class EnterpriseCreditTransactionType(str, enum.Enum):
    CREDIT_USED = "credit_used"
    CREDIT_PAID = "credit_paid"
    CREDIT_ADJUSTED = "credit_adjusted"
    CREDIT_EXPIRED = "credit_expired"


class Enterprise(BaseModel):
    __tablename__ = "enterprises"

    name = Column(String(255), nullable=False)
    legal_entity_type = Column(
        SAEnum(LegalEntityType, name="legal_entity_type_enum"),
        nullable=False,
    )
    gst_number = Column(String(20), unique=True, nullable=True)
    pan = Column(String(12), nullable=False)
    cin = Column(String(21), nullable=True)
    registered_address = Column(JSONB, nullable=False)
    office_address = Column(JSONB, nullable=True)
    contact_person_name = Column(String(255), nullable=False)
    contact_person_email = Column(String(255), nullable=False)
    contact_person_phone = Column(String(15), nullable=False)
    kyc_status = Column(
        SAEnum("pending", "in_progress", "verified", "rejected", name="enterprise_kyc_status_enum"),
        default="pending",
    )
    kyc_verified_at = Column(DateTime(timezone=True), nullable=True)
    trust_score = Column(Integer, default=0)
    credit_line_enabled = Column(Boolean, default=False)
    credit_limit_inr = Column(Numeric(12, 2), nullable=True)
    credit_used_inr = Column(Numeric(12, 2), default=0)
    credit_days = Column(Integer, default=30)
    pricelist_id = Column(UUID(as_uuid=True), ForeignKey("pricelists.id"), nullable=True)
    account_manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    total_rentals = Column(Integer, default=0)
    total_spend = Column(Numeric(14, 2), default=0)

    # Relationships
    members = relationship("EnterpriseMember", back_populates="enterprise", cascade="all, delete-orphan")
    credit_transactions = relationship("EnterpriseCreditTransaction", back_populates="enterprise", cascade="all, delete-orphan")


class EnterpriseMember(BaseModel):
    __tablename__ = "enterprise_members"

    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    sub_role = Column(
        SAEnum(EnterpriseSubRole, name="enterprise_sub_role_enum"),
        nullable=False,
    )
    department = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)
    spending_limit_inr = Column(Numeric(12, 2), nullable=True)
    monthly_limit_inr = Column(Numeric(12, 2), nullable=True)
    current_month_spend = Column(Numeric(12, 2), default=0)
    can_approve_rentals = Column(Boolean, default=False)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    invited_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    enterprise = relationship("Enterprise", back_populates="members")


class EnterpriseCreditTransaction(BaseModel):
    __tablename__ = "enterprise_credit_transactions"

    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=False)
    type = Column(
        SAEnum(EnterpriseCreditTransactionType, name="enterprise_credit_txn_type_enum"),
        nullable=False,
    )
    amount = Column(Numeric(12, 2), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True)
    reference = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    enterprise = relationship("Enterprise", back_populates="credit_transactions")
