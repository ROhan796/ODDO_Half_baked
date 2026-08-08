# app/models/crm.py
import uuid
from sqlalchemy import (
    Column, String, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, Integer, Boolean
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class CRMContactType(str, enum.Enum):
    LEAD = "lead"
    CUSTOMER = "customer"
    PARTNER = "partner"
    VENDOR = "vendor"


class CRMContactStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
    INACTIVE = "inactive"


class CRMInteractionType(str, enum.Enum):
    CALL = "call"
    EMAIL = "email"
    SMS = "sms"
    MEETING = "meeting"
    NOTE = "note"
    WHATSAPP = "whatsapp"


class CRMContact(BaseModel):
    __tablename__ = "crm_contacts"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    contact_type = Column(
        SAEnum(CRMContactType, name="crm_contact_type_enum"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(15), nullable=True)
    company = Column(String(255), nullable=True)
    designation = Column(String(255), nullable=True)
    status = Column(
        SAEnum(CRMContactStatus, name="crm_contact_status_enum"),
        default=CRMContactStatus.NEW,
    )
    source = Column(String(100), nullable=True)
    lead_score = Column(Integer, default=0)
    lifetime_value = Column(Numeric(14, 2), default=0)
    last_contact_at = Column(DateTime(timezone=True), nullable=True)
    next_follow_up_at = Column(DateTime(timezone=True), nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(Text), default=[])
    metadata_ = Column("metadata", JSONB, default={})

    interactions = relationship("CRMInteraction", back_populates="contact", cascade="all, delete-orphan")
    contact_tags = relationship("CRMContactTag", back_populates="contact", cascade="all, delete-orphan")


class CRMInteraction(BaseModel):
    __tablename__ = "crm_interactions"

    contact_id = Column(UUID(as_uuid=True), ForeignKey("crm_contacts.id", ondelete="CASCADE"), nullable=False)
    interaction_type = Column(
        SAEnum(CRMInteractionType, name="crm_interaction_type_enum"),
        nullable=False,
    )
    direction = Column(String(10), nullable=False)
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    outcome = Column(String(255), nullable=True)
    next_action = Column(String(255), nullable=True)
    next_action_at = Column(DateTime(timezone=True), nullable=True)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    attachment_urls = Column(ARRAY(Text), default=[])

    contact = relationship("CRMContact", back_populates="interactions")


class CRMTag(BaseModel):
    __tablename__ = "crm_tags"

    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), nullable=True)
    description = Column(Text, nullable=True)

    contacts = relationship("CRMContactTag", back_populates="tag", cascade="all, delete-orphan")


class CRMContactTag(BaseModel):
    __tablename__ = "crm_contact_tags"

    contact_id = Column(UUID(as_uuid=True), ForeignKey("crm_contacts.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("crm_tags.id", ondelete="CASCADE"), nullable=False)

    contact = relationship("CRMContact", back_populates="contact_tags")
    tag = relationship("CRMTag", back_populates="contacts")
