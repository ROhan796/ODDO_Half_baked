# app/models/user.py
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Date, DateTime, SmallInteger, Text, Enum as SAEnum,
    ForeignKey, Index, JSON, Integer, Numeric
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, INET, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class UserType(str, enum.Enum):
    PERSONAL = "personal"
    ENTERPRISE = "enterprise"
    ENTERPRISE_SUB = "enterprise_sub"


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    OPS_ADMIN = "ops_admin"
    FIELD_AGENT = "field_agent"
    PORTAL_USER = "portal_user"


class KYCStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    REJECTED = "rejected"


class KYCStep(str, enum.Enum):
    PHONE = "phone"
    EMAIL = "email"
    GOV_ID = "gov_id"
    SELFIE = "selfie"
    ADDRESS = "address"
    PAYMENT = "payment"
    DEVICE = "device"


class OTPChannel(str, enum.Enum):
    SMS = "sms"
    EMAIL = "email"


class OTPPurpose(str, enum.Enum):
    LOGIN = "login"
    REGISTER = "register"
    KYC = "kyc"
    TRANSACTION = "transaction"
    EXTENSION = "extension"


class User(BaseModel):
    __tablename__ = "users"

    clerk_user_id = Column(String(255), unique=True, nullable=True, index=True)
    user_type = Column(
        SAEnum(UserType, name="user_type_enum", create_type=False),
        nullable=False,
        default=UserType.PERSONAL,
    )
    role = Column(
        SAEnum(UserRole, name="user_role_enum", create_type=False),
        nullable=False,
    )
    phone = Column(String(15), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=True)
    profile_photo_url = Column(Text, nullable=True)
    kyc_status = Column(
        SAEnum(KYCStatus, name="kyc_status_enum", create_type=False),
        default=KYCStatus.PENDING,
    )
    kyc_completed_at = Column(DateTime(timezone=True), nullable=True)
    trust_score = Column(SmallInteger, default=0)
    trust_tier = Column(String(20), default="unverified")
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=True)
    blacklisted = Column(Boolean, default=False)
    blacklisted_at = Column(DateTime(timezone=True), nullable=True)
    blacklisted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    blacklist_reason = Column(Text, nullable=True)
    device_fingerprints = Column(ARRAY(Text), default=[])
    notification_preferences = Column(
        JSONB,
        default={"sms": True, "email": True, "push": True},
    )
    points_balance = Column(Integer, default=0)
    lifetime_rentals = Column(Integer, default=0)
    lifetime_spend = Column(Numeric(14, 2), default=0)
    last_rental_at = Column(DateTime(timezone=True), nullable=True)
    referral_code = Column(String(20), unique=True, nullable=True)
    referred_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    enterprise = relationship("Enterprise", foreign_keys=[enterprise_id])
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    kyc_records = relationship("KYCRecord", back_populates="user", cascade="all, delete-orphan", foreign_keys="[KYCRecord.user_id]")
    trust_history = relationship("TrustScoreHistory", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_trust_tier", "trust_tier"),
        Index("idx_users_blacklisted", "blacklisted", postgresql_where="blacklisted = true"),
        Index("idx_users_enterprise_id", "enterprise_id"),
    )


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, index=True)
    device_fingerprint = Column(Text, nullable=False)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(INET, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")


class OTPToken(BaseModel):
    __tablename__ = "otp_tokens"

    identifier = Column(String(255), nullable=False)
    channel = Column(SAEnum(OTPChannel, name="otp_channel_enum", create_type=False), nullable=False)
    code = Column(String(6), nullable=False)
    purpose = Column(SAEnum(OTPPurpose, name="otp_purpose_enum", create_type=False), nullable=False)
    attempts = Column(SmallInteger, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)


class KYCRecord(BaseModel):
    __tablename__ = "kyc_records"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    step = Column(SAEnum(KYCStep, name="kyc_step_enum", create_type=False), nullable=False)
    id_type = Column(String(20), nullable=True)
    id_number = Column(String(50), nullable=True)
    id_doc_url = Column(Text, nullable=True)
    selfie_url = Column(Text, nullable=True)
    liveness_video_url = Column(Text, nullable=True)
    face_match_score = Column(Numeric(5, 2), nullable=True)
    liveness_passed = Column(Boolean, nullable=True)
    address_doc_url = Column(Text, nullable=True)
    address_verified = Column(Boolean, nullable=True)
    payment_method_token = Column(String(255), nullable=True)
    payment_method_last4 = Column(String(4), nullable=True)
    payment_method_type = Column(String(10), nullable=True)
    device_fingerprint = Column(Text, nullable=True)
    status = Column(
        SAEnum("pending", "approved", "rejected", "manual_review", name="kyc_record_status_enum"),
        default="pending",
    )
    rejection_reason = Column(Text, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="kyc_records", foreign_keys=[user_id])


class TrustScoreHistory(BaseModel):
    __tablename__ = "trust_score_history"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    previous_score = Column(SmallInteger, nullable=False)
    new_score = Column(SmallInteger, nullable=False)
    change_amount = Column(SmallInteger, nullable=False)
    reason = Column(String(100), nullable=False)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    reference_type = Column(String(50), nullable=True)

    user = relationship("User", back_populates="trust_history")
