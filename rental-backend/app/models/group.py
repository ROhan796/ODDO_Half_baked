# app/models/group.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, SmallInteger
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class GroupStatus(str, enum.Enum):
    ACTIVE = "active"
    DISSOLVED = "dissolved"
    SUSPENDED = "suspended"


class GroupMemberRole(str, enum.Enum):
    LEADER = "leader"
    MEMBER = "member"


class GroupMemberStatus(str, enum.Enum):
    INVITED = "invited"
    ACTIVE = "active"
    REMOVED = "removed"


class GroupDepositStatus(str, enum.Enum):
    PENDING = "pending"
    COLLECTING = "collecting"
    HELD = "held"
    SETTLED = "settled"
    FORFEITED = "forfeited"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    FAILED = "failed"
    RELEASED = "released"
    FORFEITED = "forfeited"


class GroupVoteType(str, enum.Enum):
    EXTENSION = "extension"
    DISPUTE = "dispute"
    DISSOLVE = "dissolve"


class GroupVoteStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class VoteChoice(str, enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"


class Group(BaseModel):
    __tablename__ = "groups"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    leader_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    trust_score = Column(Numeric(5, 2), default=0)
    trust_tier = Column(String(20), default="unverified")
    status = Column(
        SAEnum(GroupStatus, name="group_status_enum", create_type=False),
        default=GroupStatus.ACTIVE,
    )
    max_members = Column(SmallInteger, default=20)
    current_member_count = Column(SmallInteger, default=1)
    joint_liability = Column(Boolean, default=True)
    dissolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    deposits = relationship("GroupDeposit", back_populates="group", cascade="all, delete-orphan")
    votes = relationship("GroupVote", back_populates="group", cascade="all, delete-orphan")


class GroupMember(BaseModel):
    __tablename__ = "group_members"

    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(
        SAEnum(GroupMemberRole, name="group_member_role_enum", create_type=False),
        default=GroupMemberRole.MEMBER,
    )
    status = Column(
        SAEnum(GroupMemberStatus, name="group_member_status_enum", create_type=False),
        default=GroupMemberStatus.INVITED,
    )
    deposit_share_pct = Column(Numeric(5, 2), default=0)
    deposit_share_amount = Column(Numeric(12, 2), default=0)
    trust_score_at_join = Column(SmallInteger, nullable=False)
    joined_at = Column(DateTime(timezone=True), nullable=True)
    removed_at = Column(DateTime(timezone=True), nullable=True)
    removed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    group = relationship("Group", back_populates="members")


class GroupDeposit(BaseModel):
    __tablename__ = "group_deposits"

    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), unique=True, nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    total_collected = Column(Numeric(12, 2), default=0)
    status = Column(
        SAEnum(GroupDepositStatus, name="group_deposit_status_enum", create_type=False),
        default=GroupDepositStatus.PENDING,
    )
    settled_at = Column(DateTime(timezone=True), nullable=True)

    group = relationship("Group", back_populates="deposits")
    members = relationship("GroupDepositMember", back_populates="group_deposit", cascade="all, delete-orphan")


class GroupDepositMember(BaseModel):
    __tablename__ = "group_deposit_members"

    group_deposit_id = Column(UUID(as_uuid=True), ForeignKey("group_deposits.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_status = Column(
        SAEnum(PaymentStatus, name="group_deposit_payment_status_enum", create_type=False),
        default=PaymentStatus.PENDING,
    )
    authorization_code = Column(String(255), nullable=True)
    refund_amount = Column(Numeric(12, 2), nullable=True)
    refund_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)

    group_deposit = relationship("GroupDeposit", back_populates="members")


class GroupVote(BaseModel):
    __tablename__ = "group_votes"

    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=True)
    vote_type = Column(
        SAEnum(GroupVoteType, name="group_vote_type_enum", create_type=False),
        nullable=False,
    )
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(
        SAEnum(GroupVoteStatus, name="group_vote_status_enum", create_type=False),
        default=GroupVoteStatus.PENDING,
    )
    votes_for = Column(SmallInteger, default=0)
    votes_against = Column(SmallInteger, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    group = relationship("Group", back_populates="votes")
    records = relationship("GroupVoteRecord", back_populates="vote", cascade="all, delete-orphan")


class GroupVoteRecord(BaseModel):
    __tablename__ = "group_vote_records"

    vote_id = Column(UUID(as_uuid=True), ForeignKey("group_votes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    vote = Column(
        SAEnum(VoteChoice, name="vote_choice_enum", create_type=False),
        nullable=False,
    )
    voted_at = Column(DateTime(timezone=True), nullable=True)

    vote = relationship("GroupVote", back_populates="records")
