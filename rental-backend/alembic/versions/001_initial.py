"""initial migration - create all tables

Revision ID: 001
Revises:
Create Date: 2026-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_type_enum = postgresql.ENUM(
        "personal", "enterprise", "enterprise_sub",
        name="user_type_enum", create_type=False,
    )
    user_role_enum = postgresql.ENUM(
        "super_admin", "ops_admin", "field_agent", "portal_user",
        name="user_role_enum", create_type=False,
    )
    kyc_status_enum = postgresql.ENUM(
        "pending", "in_progress", "verified", "rejected",
        name="kyc_status_enum", create_type=False,
    )
    kyc_step_enum = postgresql.ENUM(
        "phone", "email", "gov_id", "selfie", "address", "payment", "device",
        name="kyc_step_enum", create_type=False,
    )
    otp_channel_enum = postgresql.ENUM(
        "sms", "email",
        name="otp_channel_enum", create_type=False,
    )
    otp_purpose_enum = postgresql.ENUM(
        "login", "register", "kyc", "transaction", "extension",
        name="otp_purpose_enum", create_type=False,
    )
    kyc_record_status_enum = postgresql.ENUM(
        "pending", "approved", "rejected", "manual_review",
        name="kyc_record_status_enum", create_type=False,
    )
    legal_entity_type_enum = postgresql.ENUM(
        "private_ltd", "llp", "partnership", "proprietorship", "ngo",
        name="legal_entity_type_enum", create_type=False,
    )
    enterprise_sub_role_enum = postgresql.ENUM(
        "admin", "procurement", "department_user", "auditor",
        name="enterprise_sub_role_enum", create_type=False,
    )
    enterprise_kyc_status_enum = postgresql.ENUM(
        "pending", "in_progress", "verified", "rejected",
        name="enterprise_kyc_status_enum", create_type=False,
    )
    enterprise_credit_txn_type_enum = postgresql.ENUM(
        "credit_used", "credit_paid", "credit_adjusted", "credit_expired",
        name="enterprise_credit_txn_type_enum", create_type=False,
    )
    group_status_enum = postgresql.ENUM(
        "active", "dissolved", "suspended",
        name="group_status_enum", create_type=False,
    )
    group_member_role_enum = postgresql.ENUM(
        "leader", "member",
        name="group_member_role_enum", create_type=False,
    )
    group_member_status_enum = postgresql.ENUM(
        "invited", "active", "removed",
        name="group_member_status_enum", create_type=False,
    )
    group_deposit_status_enum = postgresql.ENUM(
        "pending", "collecting", "held", "settled", "forfeited",
        name="group_deposit_status_enum", create_type=False,
    )
    group_deposit_payment_status_enum = postgresql.ENUM(
        "pending", "authorized", "failed", "released", "forfeited",
        name="group_deposit_payment_status_enum", create_type=False,
    )
    group_vote_type_enum = postgresql.ENUM(
        "extension", "dispute", "dissolve",
        name="group_vote_type_enum", create_type=False,
    )
    group_vote_status_enum = postgresql.ENUM(
        "pending", "approved", "rejected", "expired",
        name="group_vote_status_enum", create_type=False,
    )
    vote_choice_enum = postgresql.ENUM(
        "approve", "reject",
        name="vote_choice_enum", create_type=False,
    )
    product_status_enum = postgresql.ENUM(
        "available", "rented", "in_repair", "inactive", "archived",
        name="product_status_enum", create_type=False,
    )
    late_fee_mode_enum = postgresql.ENUM(
        "hourly", "daily", "weekly", "monthly",
        name="late_fee_mode_enum", create_type=False,
    )
    block_type_enum = postgresql.ENUM(
        "rental", "maintenance", "reservation", "blackout",
        name="block_type_enum", create_type=False,
    )
    block_status_enum = postgresql.ENUM(
        "active", "cancelled", "completed",
        name="block_status_enum", create_type=False,
    )
    reservation_status_enum = postgresql.ENUM(
        "pending", "confirmed", "expired", "cancelled",
        name="reservation_status_enum", create_type=False,
    )
    rental_status_enum = postgresql.ENUM(
        "pending", "confirmed", "active", "returned", "overdue", "cancelled",
        name="rental_status_enum", create_type=False,
    )
    rental_type_enum = postgresql.ENUM(
        "daily", "weekly", "monthly",
        name="rental_type_enum", create_type=False,
    )
    extension_status_enum = postgresql.ENUM(
        "pending", "approved", "rejected",
        name="extension_status_enum", create_type=False,
    )
    quotation_status_enum = postgresql.ENUM(
        "draft", "sent", "accepted", "rejected", "expired", "converted",
        name="quotation_status_enum", create_type=False,
    )
    invoice_status_enum = postgresql.ENUM(
        "draft", "pending", "paid", "partially_paid", "overdue", "cancelled", "refunded",
        name="invoice_status_enum", create_type=False,
    )
    payment_status_enum = postgresql.ENUM(
        "pending", "processing", "completed", "failed", "refunded",
        name="payment_status_enum", create_type=False,
    )
    payment_method_enum = postgresql.ENUM(
        "razorpay", "cash", "bank_transfer", "credit",
        name="payment_method_enum", create_type=False,
    )
    deposit_status_enum = postgresql.ENUM(
        "pending", "authorized", "captured", "settled",
        "partially_deducted", "forfeited", "refunded",
        name="deposit_status_enum", create_type=False,
    )
    deduction_type_enum = postgresql.ENUM(
        "late_fee", "damage", "missing_item", "other",
        name="deduction_type_enum", create_type=False,
    )
    custody_event_type_enum = postgresql.ENUM(
        "checkout", "checkin", "transfer", "inspection",
        name="custody_event_type_enum", create_type=False,
    )
    late_fee_status_enum = postgresql.ENUM(
        "calculated", "applied", "waived", "disputed", "partially_waived",
        name="late_fee_status_enum", create_type=False,
    )
    dispute_type_enum = postgresql.ENUM(
        "late_fee", "damage", "deposit", "charge", "other",
        name="dispute_type_enum", create_type=False,
    )
    dispute_status_enum = postgresql.ENUM(
        "open", "under_review", "resolved", "escalated", "closed",
        name="dispute_status_enum", create_type=False,
    )
    dispute_resolution_enum = postgresql.ENUM(
        "favor_customer", "favor_company", "partial", "withdrawn",
        name="dispute_resolution_enum", create_type=False,
    )
    repair_status_enum = postgresql.ENUM(
        "reported", "assessed", "in_progress", "completed", "write_off",
        name="repair_status_enum", create_type=False,
    )
    recovery_status_enum = postgresql.ENUM(
        "initiated", "in_progress", "successful", "partial", "failed", "legal",
        name="recovery_status_enum", create_type=False,
    )
    blacklist_reason_enum = postgresql.ENUM(
        "payment_fraud", "identity_fraud", "theft", "damage", "non_payment", "other",
        name="blacklist_reason_enum", create_type=False,
    )
    notification_type_enum = postgresql.ENUM(
        "rental", "payment", "reminder", "system", "marketing",
        name="notification_type_enum", create_type=False,
    )
    notification_channel_enum = postgresql.ENUM(
        "sms", "email", "push", "in_app",
        name="notification_channel_enum", create_type=False,
    )
    notification_status_enum = postgresql.ENUM(
        "pending", "sent", "delivered", "failed", "read",
        name="notification_status_enum", create_type=False,
    )
    notification_template_type_enum = postgresql.ENUM(
        "rental", "payment", "reminder", "system", "marketing",
        name="notification_template_type_enum", create_type=False,
    )
    notification_template_channel_enum = postgresql.ENUM(
        "sms", "email", "push", "in_app",
        name="notification_template_channel_enum", create_type=False,
    )
    crm_contact_type_enum = postgresql.ENUM(
        "lead", "customer", "partner", "vendor",
        name="crm_contact_type_enum", create_type=False,
    )
    crm_contact_status_enum = postgresql.ENUM(
        "new", "contacted", "qualified", "proposal",
        "negotiation", "won", "lost", "inactive",
        name="crm_contact_status_enum", create_type=False,
    )
    crm_interaction_type_enum = postgresql.ENUM(
        "call", "email", "sms", "meeting", "note", "whatsapp",
        name="crm_interaction_type_enum", create_type=False,
    )
    stock_movement_type_enum = postgresql.ENUM(
        "in", "out", "transfer", "adjustment", "return",
        name="stock_movement_type_enum", create_type=False,
    )
    points_transaction_type_enum = postgresql.ENUM(
        "earned", "redeemed", "expired", "adjusted", "referral",
        name="points_transaction_type_enum", create_type=False,
    )
    referral_status_enum = postgresql.ENUM(
        "pending", "completed", "expired",
        name="referral_status_enum", create_type=False,
    )
    audit_action_enum = postgresql.ENUM(
        "create", "read", "update", "delete",
        "login", "logout", "export", "approve", "reject",
        name="audit_action_enum", create_type=False,
    )

    for e in [
        user_type_enum, user_role_enum, kyc_status_enum, kyc_step_enum,
        otp_channel_enum, otp_purpose_enum, kyc_record_status_enum,
        legal_entity_type_enum, enterprise_sub_role_enum, enterprise_kyc_status_enum,
        enterprise_credit_txn_type_enum, group_status_enum, group_member_role_enum,
        group_member_status_enum, group_deposit_status_enum,
        group_deposit_payment_status_enum, group_vote_type_enum,
        group_vote_status_enum, vote_choice_enum, product_status_enum,
        late_fee_mode_enum, block_type_enum, block_status_enum,
        reservation_status_enum, rental_status_enum, rental_type_enum,
        extension_status_enum, quotation_status_enum, invoice_status_enum,
        payment_status_enum, payment_method_enum, deposit_status_enum,
        deduction_type_enum, custody_event_type_enum, late_fee_status_enum,
        dispute_type_enum, dispute_status_enum, dispute_resolution_enum,
        repair_status_enum, recovery_status_enum, blacklist_reason_enum,
        notification_type_enum, notification_channel_enum, notification_status_enum,
        notification_template_type_enum, notification_template_channel_enum,
        crm_contact_type_enum, crm_contact_status_enum, crm_interaction_type_enum,
        stock_movement_type_enum, points_transaction_type_enum,
        referral_status_enum, audit_action_enum,
    ]:
        e.create(op.get_bind(), checkfirst=True)

    # ============================================================
    # users
    # ============================================================
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_type", sa.Enum(name="user_type_enum", create_type=False), nullable=False, server_default="personal"),
        sa.Column("role", sa.Enum(name="user_role_enum", create_type=False), nullable=False),
        sa.Column("phone", sa.String(15), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("dob", sa.Date, nullable=True),
        sa.Column("profile_photo_url", sa.Text, nullable=True),
        sa.Column("kyc_status", sa.Enum(name="kyc_status_enum", create_type=False), server_default="pending"),
        sa.Column("kyc_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trust_score", sa.SmallInteger, server_default="0"),
        sa.Column("trust_tier", sa.String(20), server_default="unverified"),
        sa.Column("enterprise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("enterprises.id"), nullable=True),
        sa.Column("blacklisted", sa.Boolean, server_default="false"),
        sa.Column("blacklisted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("blacklisted_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("blacklist_reason", sa.Text, nullable=True),
        sa.Column("device_fingerprints", postgresql.ARRAY(sa.Text), server_default="{}"),
        sa.Column("notification_preferences", postgresql.JSONB, server_default='{"sms": true, "email": true, "push": true}'),
        sa.Column("points_balance", sa.Integer, server_default="0"),
        sa.Column("lifetime_rentals", sa.Integer, server_default="0"),
        sa.Column("lifetime_spend", sa.Numeric(14, 2), server_default="0"),
        sa.Column("last_rental_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("referral_code", sa.String(20), unique=True, nullable=True),
        sa.Column("referred_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("idx_users_trust_tier", "users", ["trust_tier"])
    op.create_index(
        "idx_users_blacklisted", "users", ["blacklisted"],
        postgresql_where="blacklisted = true",
    )
    op.create_index("idx_users_enterprise_id", "users", ["enterprise_id"])

    # ============================================================
    # refresh_tokens
    # ============================================================
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False, index=True),
        sa.Column("device_fingerprint", sa.Text, nullable=False),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("ip_address", postgresql.INET, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # otp_tokens
    # ============================================================
    op.create_table(
        "otp_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("identifier", sa.String(255), nullable=False),
        sa.Column("channel", sa.Enum(name="otp_channel_enum", create_type=False), nullable=False),
        sa.Column("code", sa.String(6), nullable=False),
        sa.Column("purpose", sa.Enum(name="otp_purpose_enum", create_type=False), nullable=False),
        sa.Column("attempts", sa.SmallInteger, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # kyc_records
    # ============================================================
    op.create_table(
        "kyc_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step", sa.Enum(name="kyc_step_enum", create_type=False), nullable=False),
        sa.Column("id_type", sa.String(20), nullable=True),
        sa.Column("id_number", sa.String(50), nullable=True),
        sa.Column("id_doc_url", sa.Text, nullable=True),
        sa.Column("selfie_url", sa.Text, nullable=True),
        sa.Column("liveness_video_url", sa.Text, nullable=True),
        sa.Column("face_match_score", sa.Float, nullable=True),
        sa.Column("liveness_passed", sa.Boolean, nullable=True),
        sa.Column("address_doc_url", sa.Text, nullable=True),
        sa.Column("address_verified", sa.Boolean, nullable=True),
        sa.Column("payment_method_token", sa.String(255), nullable=True),
        sa.Column("payment_method_last4", sa.String(4), nullable=True),
        sa.Column("payment_method_type", sa.String(10), nullable=True),
        sa.Column("device_fingerprint", sa.Text, nullable=True),
        sa.Column("status", sa.Enum(name="kyc_record_status_enum", create_type=False), server_default="pending"),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # trust_score_history
    # ============================================================
    op.create_table(
        "trust_score_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("previous_score", sa.SmallInteger, nullable=False),
        sa.Column("new_score", sa.SmallInteger, nullable=False),
        sa.Column("change_amount", sa.SmallInteger, nullable=False),
        sa.Column("reason", sa.String(100), nullable=False),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reference_type", sa.String(50), nullable=True),
    )

    # ============================================================
    # pricelists
    # ============================================================
    op.create_table(
        "pricelists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_default", sa.Boolean, server_default="false"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    )

    # ============================================================
    # enterprises
    # ============================================================
    op.create_table(
        "enterprises",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("legal_entity_type", sa.Enum(name="legal_entity_type_enum", create_type=False), nullable=False),
        sa.Column("gst_number", sa.String(20), unique=True, nullable=True),
        sa.Column("pan", sa.String(12), nullable=False),
        sa.Column("cin", sa.String(21), nullable=True),
        sa.Column("registered_address", postgresql.JSONB, nullable=False),
        sa.Column("office_address", postgresql.JSONB, nullable=True),
        sa.Column("contact_person_name", sa.String(255), nullable=False),
        sa.Column("contact_person_email", sa.String(255), nullable=False),
        sa.Column("contact_person_phone", sa.String(15), nullable=False),
        sa.Column("kyc_status", sa.Enum(name="enterprise_kyc_status_enum", create_type=False), server_default="pending"),
        sa.Column("kyc_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trust_score", sa.Integer, server_default="0"),
        sa.Column("credit_line_enabled", sa.Boolean, server_default="false"),
        sa.Column("credit_limit_inr", sa.Numeric(12, 2), nullable=True),
        sa.Column("credit_used_inr", sa.Numeric(12, 2), server_default="0"),
        sa.Column("credit_days", sa.Integer, server_default="30"),
        sa.Column("pricelist_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pricelists.id"), nullable=True),
        sa.Column("account_manager_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("total_rentals", sa.Integer, server_default="0"),
        sa.Column("total_spend", sa.Numeric(14, 2), server_default="0"),
    )

    # ============================================================
    # enterprise_members
    # ============================================================
    op.create_table(
        "enterprise_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("enterprise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("enterprises.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("sub_role", sa.Enum(name="enterprise_sub_role_enum", create_type=False), nullable=False),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("designation", sa.String(100), nullable=True),
        sa.Column("spending_limit_inr", sa.Numeric(12, 2), nullable=True),
        sa.Column("monthly_limit_inr", sa.Numeric(12, 2), nullable=True),
        sa.Column("current_month_spend", sa.Numeric(12, 2), server_default="0"),
        sa.Column("can_approve_rentals", sa.Boolean, server_default="false"),
        sa.Column("invited_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("invited_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # enterprise_credit_transactions
    # ============================================================
    op.create_table(
        "enterprise_credit_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("enterprise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("enterprises.id"), nullable=False),
        sa.Column("type", sa.Enum(name="enterprise_credit_txn_type_enum", create_type=False), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("invoices.id"), nullable=True),
        sa.Column("reference", sa.Text, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    )

    # ============================================================
    # groups
    # ============================================================
    op.create_table(
        "groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("leader_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("trust_score", sa.Numeric(5, 2), server_default="0"),
        sa.Column("trust_tier", sa.String(20), server_default="unverified"),
        sa.Column("status", sa.Enum(name="group_status_enum", create_type=False), server_default="active"),
        sa.Column("max_members", sa.SmallInteger, server_default="20"),
        sa.Column("current_member_count", sa.SmallInteger, server_default="1"),
        sa.Column("joint_liability", sa.Boolean, server_default="true"),
        sa.Column("dissolved_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # group_members
    # ============================================================
    op.create_table(
        "group_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.Enum(name="group_member_role_enum", create_type=False), server_default="member"),
        sa.Column("status", sa.Enum(name="group_member_status_enum", create_type=False), server_default="invited"),
        sa.Column("deposit_share_pct", sa.Numeric(5, 2), server_default="0"),
        sa.Column("deposit_share_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("trust_score_at_join", sa.SmallInteger, nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("removed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )

    # ============================================================
    # group_deposits
    # ============================================================
    op.create_table(
        "group_deposits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), unique=True, nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_collected", sa.Numeric(12, 2), server_default="0"),
        sa.Column("status", sa.Enum(name="group_deposit_status_enum", create_type=False), server_default="pending"),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # group_deposit_members
    # ============================================================
    op.create_table(
        "group_deposit_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("group_deposit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("group_deposits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_status", sa.Enum(name="group_deposit_payment_status_enum", create_type=False), server_default="pending"),
        sa.Column("authorization_code", sa.String(255), nullable=True),
        sa.Column("refund_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("refund_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # group_votes
    # ============================================================
    op.create_table(
        "group_votes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), nullable=True),
        sa.Column("vote_type", sa.Enum(name="group_vote_type_enum", create_type=False), nullable=False),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("status", sa.Enum(name="group_vote_status_enum", create_type=False), server_default="pending"),
        sa.Column("votes_for", sa.SmallInteger, server_default="0"),
        sa.Column("votes_against", sa.SmallInteger, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # group_vote_records
    # ============================================================
    op.create_table(
        "group_vote_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("vote_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("group_votes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("vote", sa.Enum(name="vote_choice_enum", create_type=False), nullable=False),
        sa.Column("voted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # categories
    # ============================================================
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("icon_url", sa.Text, nullable=True),
        sa.Column("deposit_percentage_override", sa.Numeric(5, 2), nullable=True),
        sa.Column("late_fee_rate_override", sa.Numeric(10, 2), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("sort_order", sa.Integer, server_default="0"),
    )

    # ============================================================
    # products
    # ============================================================
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("short_description", sa.String(500), nullable=True),
        sa.Column("serial_number", sa.String(100), unique=True, nullable=True),
        sa.Column("qr_code", sa.String(255), unique=True, nullable=True),
        sa.Column("rfid_tag", sa.String(100), nullable=True),
        sa.Column("barcode", sa.String(100), nullable=True),
        sa.Column("sku", sa.String(100), unique=True, nullable=True),
        sa.Column("status", sa.Enum(name="product_status_enum", create_type=False), server_default="available"),
        sa.Column("current_holder_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("current_rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), nullable=True),
        sa.Column("condition_rating", sa.SmallInteger, server_default="5"),
        sa.Column("condition_notes", sa.Text, nullable=True),
        sa.Column("purchase_date", sa.Date, nullable=True),
        sa.Column("purchase_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("current_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("depreciation_rate", sa.Numeric(5, 2), server_default="0"),
        sa.Column("insurance_expiry", sa.Date, nullable=True),
        sa.Column("warranty_expiry", sa.Date, nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("is_insured", sa.Boolean, server_default="false"),
        sa.Column("deposit_percentage", sa.Numeric(5, 2), server_default="30.00"),
        sa.Column("late_fee_rate", sa.Numeric(10, 2), nullable=True),
        sa.Column("late_fee_mode", sa.Enum(name="late_fee_mode_enum", create_type=False), server_default="daily"),
        sa.Column("grace_period_minutes", sa.Integer, server_default="30"),
        sa.Column("max_late_fee_multiplier", sa.Numeric(3, 1), server_default="2.0"),
        sa.Column("min_rental_duration", sa.Integer, server_default="1"),
        sa.Column("max_rental_duration", sa.Integer, nullable=True),
        sa.Column("images", postgresql.ARRAY(sa.Text), server_default="{}"),
        sa.Column("thumbnail_url", sa.Text, nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.Text), server_default="{}"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("total_rentals", sa.Integer, server_default="0"),
        sa.Column("total_revenue", sa.Numeric(14, 2), server_default="0"),
        sa.Column("total_damage_reports", sa.Integer, server_default="0"),
        sa.Column("is_featured", sa.Boolean, server_default="false"),
        sa.Column("sort_order", sa.Integer, server_default="0"),
    )

    # ============================================================
    # product_variants
    # ============================================================
    op.create_table(
        "product_variants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("attribute", sa.String(50), nullable=False),
        sa.Column("value", sa.String(100), nullable=False),
        sa.Column("sku", sa.String(100), unique=True, nullable=True),
        sa.Column("additional_price_inr", sa.Numeric(10, 2), server_default="0"),
        sa.Column("is_default", sa.Boolean, server_default="false"),
    )

    # ============================================================
    # accessories
    # ============================================================
    op.create_table(
        "accessories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("item_code", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("replacement_cost_inr", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_required", sa.Boolean, server_default="true"),
        sa.Column("condition_rating", sa.SmallInteger, server_default="5"),
        sa.Column("image_url", sa.Text, nullable=True),
    )

    # ============================================================
    # availability_blocks
    # ============================================================
    op.create_table(
        "availability_blocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("block_type", sa.Enum(name="block_type_enum", create_type=False), nullable=False),
        sa.Column("rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.Enum(name="block_status_enum", create_type=False), server_default="active"),
        sa.Column("booked_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
    )

    # ============================================================
    # blackout_dates
    # ============================================================
    op.create_table(
        "blackout_dates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("reason", sa.String(255), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    )

    # ============================================================
    # quotations
    # ============================================================
    op.create_table(
        "quotations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("quote_number", sa.String(50), unique=True, nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("enterprise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("enterprises.id"), nullable=True),
        sa.Column("status", sa.Enum(name="quotation_status_enum", create_type=False), server_default="draft"),
        sa.Column("items", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("discount_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("terms", sa.Text, nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        sa.Column("converted_to_rental", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    )

    # ============================================================
    # quotation_templates
    # ============================================================
    op.create_table(
        "quotation_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("template_data", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("is_default", sa.Boolean, server_default="false"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    )

    # ============================================================
    # rentals
    # ============================================================
    op.create_table(
        "rentals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quotation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quotations.id"), nullable=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.Enum(name="rental_status_enum", create_type=False), server_default="pending"),
        sa.Column("rental_type", sa.Enum(name="rental_type_enum", create_type=False), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("actual_return_date", sa.Date, nullable=True),
        sa.Column("daily_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("late_fees", sa.Numeric(12, 2), server_default="0"),
        sa.Column("damage_charges", sa.Numeric(12, 2), server_default="0"),
        sa.Column("discount_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("insurance_selected", sa.Boolean, server_default="false"),
        sa.Column("insurance_amount", sa.Numeric(10, 2), server_default="0"),
        sa.Column("delivery_address", sa.Text, nullable=True),
        sa.Column("special_requirements", sa.Text, nullable=True),
        sa.Column("confirmed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("returned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("condition_at_checkout", sa.Text, nullable=True),
        sa.Column("condition_at_return", sa.Text, nullable=True),
        sa.Column("checkout_photos", sa.Text, nullable=True),
        sa.Column("return_photos", sa.Text, nullable=True),
    )

    # ============================================================
    # rental_extensions
    # ============================================================
    op.create_table(
        "rental_extensions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_end_date", sa.Date, nullable=False),
        sa.Column("new_end_date", sa.Date, nullable=False),
        sa.Column("extension_days", sa.Integer, nullable=False),
        sa.Column("additional_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.Enum(name="extension_status_enum", create_type=False), server_default="pending"),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
    )

    # ============================================================
    # reservations
    # ============================================================
    op.create_table(
        "reservations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.Enum(name="reservation_status_enum", create_type=False), server_default="pending"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quotation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quotations.id"), nullable=True),
    )

    # ============================================================
    # invoices
    # ============================================================
    op.create_table(
        "invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("invoice_number", sa.String(50), unique=True, nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("enterprise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("enterprises.id"), nullable=True),
        sa.Column("rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), nullable=True),
        sa.Column("status", sa.Enum(name="invoice_status_enum", create_type=False), server_default="draft"),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("discount_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("paid_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("billing_address", postgresql.JSONB, nullable=True),
        sa.Column("shipping_address", postgresql.JSONB, nullable=True),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
    )

    # ============================================================
    # invoice_items
    # ============================================================
    op.create_table(
        "invoice_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_rate", sa.Numeric(5, 2), server_default="0"),
        sa.Column("tax_amount", sa.Numeric(10, 2), server_default="0"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
    )

    # ============================================================
    # payments
    # ============================================================
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("payment_number", sa.String(50), unique=True, nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("invoices.id"), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.Enum(name="payment_status_enum", create_type=False), server_default="pending"),
        sa.Column("payment_method", sa.Enum(name="payment_method_enum", create_type=False), nullable=False),
        sa.Column("razorpay_order_id", sa.String(255), nullable=True),
        sa.Column("razorpay_payment_id", sa.String(255), nullable=True),
        sa.Column("razorpay_signature", sa.String(255), nullable=True),
        sa.Column("transaction_reference", sa.String(255), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refund_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("refund_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refund_reason", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
    )

    # ============================================================
    # security_deposits
    # ============================================================
    op.create_table(
        "security_deposits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), unique=True, nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.Enum(name="deposit_status_enum", create_type=False), server_default="pending"),
        sa.Column("authorization_code", sa.String(255), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refund_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("refund_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refund_reference", sa.String(255), nullable=True),
    )

    # ============================================================
    # deposit_deductions
    # ============================================================
    op.create_table(
        "deposit_deductions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deposit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("security_deposits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("reason", sa.String(255), nullable=False),
        sa.Column("deduction_type", sa.Enum(name="deduction_type_enum", create_type=False), nullable=False),
        sa.Column("documented_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("documentation_url", sa.Text, nullable=True),
        sa.Column("customer_notified", sa.Boolean, server_default="false"),
        sa.Column("customer_disputed", sa.Boolean, server_default="false"),
        sa.Column("dispute_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("disputes.id"), nullable=True),
    )

    # ============================================================
    # custody_events
    # ============================================================
    op.create_table(
        "custody_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("event_type", sa.Enum(name="custody_event_type_enum", create_type=False), nullable=False),
        sa.Column("from_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("to_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("condition_rating", sa.SmallInteger, nullable=True),
        sa.Column("condition_notes", sa.Text, nullable=True),
        sa.Column("photos", sa.Text, nullable=True),
        sa.Column("performed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    )

    # ============================================================
    # accessory_checks
    # ============================================================
    op.create_table(
        "accessory_checks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), nullable=False),
        sa.Column("accessory_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accessories.id"), nullable=False),
        sa.Column("checked_out", sa.Boolean, nullable=False),
        sa.Column("returned", sa.Boolean, nullable=True),
        sa.Column("condition_at_checkout", sa.SmallInteger, nullable=True),
        sa.Column("condition_at_return", sa.SmallInteger, nullable=True),
        sa.Column("missing", sa.Boolean, server_default="false"),
        sa.Column("damage_charged", sa.Numeric(10, 2), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
    )

    # ============================================================
    # late_fees
    # ============================================================
    op.create_table(
        "late_fees",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("days_overdue", sa.Numeric(10, 2), nullable=False),
        sa.Column("daily_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("waived_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("status", sa.Enum(name="late_fee_status_enum", create_type=False), server_default="calculated"),
        sa.Column("waived_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("waived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("waiver_reason", sa.Text, nullable=True),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("invoices.id"), nullable=True),
        sa.Column("dispute_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("disputes.id"), nullable=True),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # disputes
    # ============================================================
    op.create_table(
        "disputes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("filed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("dispute_type", sa.Enum(name="dispute_type_enum", create_type=False), nullable=False),
        sa.Column("amount_disputed", sa.Numeric(12, 2), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("evidence_urls", postgresql.ARRAY(sa.Text), server_default="{}"),
        sa.Column("status", sa.Enum(name="dispute_status_enum", create_type=False), server_default="open"),
        sa.Column("resolution", sa.Enum(name="dispute_resolution_enum", create_type=False), nullable=True),
        sa.Column("resolution_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("resolution_notes", sa.Text, nullable=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # repair_cases
    # ============================================================
    op.create_table(
        "repair_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), nullable=True),
        sa.Column("reported_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("damage_description", sa.Text, nullable=False),
        sa.Column("damage_photos", postgresql.ARRAY(sa.Text), server_default="{}"),
        sa.Column("estimated_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("actual_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("status", sa.Enum(name="repair_status_enum", create_type=False), server_default="reported"),
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column("vendor_name", sa.String(255), nullable=True),
        sa.Column("vendor_reference", sa.String(255), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("charged_to_customer", sa.Boolean, server_default="false"),
        sa.Column("customer_charge_amount", sa.Numeric(12, 2), nullable=True),
    )

    # ============================================================
    # recovery_cases
    # ============================================================
    op.create_table(
        "recovery_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rentals.id"), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("initiated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("initiated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reason", sa.String(255), nullable=False),
        sa.Column("amount_outstanding", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.Enum(name="recovery_status_enum", create_type=False), server_default="initiated"),
        sa.Column("recovery_agent", sa.String(255), nullable=True),
        sa.Column("contact_attempts", postgresql.ARRAY(sa.Text), server_default="{}"),
        sa.Column("last_contact_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_action_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_action_description", sa.Text, nullable=True),
        sa.Column("recovered_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("recovered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("product_recovered", sa.Boolean, server_default="false"),
        sa.Column("product_recovered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("escalated_to_legal", sa.Boolean, server_default="false"),
        sa.Column("legal_reference", sa.String(255), nullable=True),
    )

    # ============================================================
    # blacklists
    # ============================================================
    op.create_table(
        "blacklists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reason", sa.Enum(name="blacklist_reason_enum", create_type=False), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("evidence_urls", sa.Text, nullable=True),
        sa.Column("added_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_permanent", sa.Boolean, server_default="false"),
        sa.Column("removed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("removal_reason", sa.Text, nullable=True),
    )

    # ============================================================
    # notifications
    # ============================================================
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.Enum(name="notification_type_enum", create_type=False), nullable=False),
        sa.Column("channel", sa.Enum(name="notification_channel_enum", create_type=False), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("data", postgresql.JSONB, server_default="{}"),
        sa.Column("status", sa.Enum(name="notification_status_enum", create_type=False), server_default="pending"),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("retry_count", sa.Integer, server_default="0"),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reference_type", sa.String(50), nullable=True),
    )

    # ============================================================
    # notification_templates
    # ============================================================
    op.create_table(
        "notification_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("type", sa.Enum(name="notification_template_type_enum", create_type=False), nullable=False),
        sa.Column("channel", sa.Enum(name="notification_template_channel_enum", create_type=False), nullable=False),
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("body_template", sa.Text, nullable=False),
        sa.Column("variables", postgresql.JSONB, server_default="[]"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
    )

    # ============================================================
    # pricelist_items
    # ============================================================
    op.create_table(
        "pricelist_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("pricelist_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pricelists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("rental_type", sa.String(20), nullable=False),
        sa.Column("base_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="INR"),
        sa.Column("min_duration", sa.Integer, server_default="1"),
        sa.Column("max_duration", sa.Integer, nullable=True),
        sa.Column("deposit_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("late_fee_rate", sa.Numeric(10, 2), nullable=True),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
    )

    # ============================================================
    # crm_contacts
    # ============================================================
    op.create_table(
        "crm_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("contact_type", sa.Enum(name="crm_contact_type_enum", create_type=False), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(15), nullable=True),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column("designation", sa.String(255), nullable=True),
        sa.Column("status", sa.Enum(name="crm_contact_status_enum", create_type=False), server_default="new"),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("lead_score", sa.Integer, server_default="0"),
        sa.Column("lifetime_value", sa.Numeric(14, 2), server_default="0"),
        sa.Column("last_contact_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_follow_up_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.Text), server_default="{}"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
    )

    # ============================================================
    # crm_interactions
    # ============================================================
    op.create_table(
        "crm_interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_contacts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("interaction_type", sa.Enum(name="crm_interaction_type_enum", create_type=False), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("outcome", sa.String(255), nullable=True),
        sa.Column("next_action", sa.String(255), nullable=True),
        sa.Column("next_action_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("performed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("attachment_urls", postgresql.ARRAY(sa.Text), server_default="{}"),
    )

    # ============================================================
    # crm_tags
    # ============================================================
    op.create_table(
        "crm_tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
    )

    # ============================================================
    # crm_contact_tags
    # ============================================================
    op.create_table(
        "crm_contact_tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_contacts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_tags.id", ondelete="CASCADE"), nullable=False),
    )

    # ============================================================
    # stock_locations
    # ============================================================
    op.create_table(
        "stock_locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("pincode", sa.String(10), nullable=True),
        sa.Column("contact_person", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(15), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("is_warehouse", sa.Boolean, server_default="false"),
        sa.Column("capacity", sa.Integer, nullable=True),
    )

    # ============================================================
    # stock_movements
    # ============================================================
    op.create_table(
        "stock_movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("from_location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stock_locations.id"), nullable=True),
        sa.Column("to_location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stock_locations.id"), nullable=True),
        sa.Column("movement_type", sa.Enum(name="stock_movement_type_enum", create_type=False), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("performed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    )

    # ============================================================
    # stock_levels
    # ============================================================
    op.create_table(
        "stock_levels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stock_locations.id"), nullable=False),
        sa.Column("quantity", sa.Integer, server_default="0"),
        sa.Column("reserved", sa.Integer, server_default="0"),
        sa.Column("available", sa.Integer, server_default="0"),
        sa.Column("min_stock", sa.Integer, server_default="0"),
        sa.Column("max_stock", sa.Integer, nullable=True),
        sa.Column("last_counted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_received_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # loyalty_points_ledger
    # ============================================================
    op.create_table(
        "loyalty_points_ledger",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("transaction_type", sa.Enum(name="points_transaction_type_enum", create_type=False), nullable=False),
        sa.Column("points", sa.Integer, nullable=False),
        sa.Column("balance_after", sa.Integer, nullable=False),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # referrals
    # ============================================================
    op.create_table(
        "referrals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("referrer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("referred_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("referral_code", sa.String(20), nullable=False),
        sa.Column("status", sa.Enum(name="referral_status_enum", create_type=False), server_default="pending"),
        sa.Column("referrer_bonus_points", sa.Integer, server_default="0"),
        sa.Column("referred_bonus_points", sa.Integer, server_default="0"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ============================================================
    # audit_logs
    # ============================================================
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.Enum(name="audit_action_enum", create_type=False), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("changes", postgresql.JSONB, server_default="{}"),
        sa.Column("ip_address", postgresql.INET, nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("request_id", sa.String(36), nullable=True),
        sa.Column("session_id", sa.String(255), nullable=True),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("referrals")
    op.drop_table("loyalty_points_ledger")
    op.drop_table("stock_levels")
    op.drop_table("stock_movements")
    op.drop_table("stock_locations")
    op.drop_table("crm_contact_tags")
    op.drop_table("crm_tags")
    op.drop_table("crm_interactions")
    op.drop_table("crm_contacts")
    op.drop_table("pricelist_items")
    op.drop_table("notification_templates")
    op.drop_table("notifications")
    op.drop_table("blacklists")
    op.drop_table("recovery_cases")
    op.drop_table("repair_cases")
    op.drop_table("disputes")
    op.drop_table("late_fees")
    op.drop_table("accessory_checks")
    op.drop_table("custody_events")
    op.drop_table("deposit_deductions")
    op.drop_table("security_deposits")
    op.drop_table("payments")
    op.drop_table("invoice_items")
    op.drop_table("invoices")
    op.drop_table("reservations")
    op.drop_table("rental_extensions")
    op.drop_table("rentals")
    op.drop_table("quotation_templates")
    op.drop_table("quotations")
    op.drop_table("blackout_dates")
    op.drop_table("availability_blocks")
    op.drop_table("accessories")
    op.drop_table("product_variants")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("group_vote_records")
    op.drop_table("group_votes")
    op.drop_table("group_deposit_members")
    op.drop_table("group_deposits")
    op.drop_table("group_members")
    op.drop_table("groups")
    op.drop_table("enterprise_credit_transactions")
    op.drop_table("enterprise_members")
    op.drop_table("enterprises")
    op.drop_table("pricelists")
    op.drop_table("trust_score_history")
    op.drop_table("kyc_records")
    op.drop_table("otp_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("users")

    for e_name in [
        "audit_action_enum", "referral_status_enum", "points_transaction_type_enum",
        "stock_movement_type_enum", "crm_interaction_type_enum",
        "crm_contact_status_enum", "crm_contact_type_enum",
        "notification_template_channel_enum", "notification_template_type_enum",
        "notification_status_enum", "notification_channel_enum", "notification_type_enum",
        "blacklist_reason_enum", "recovery_status_enum", "repair_status_enum",
        "dispute_resolution_enum", "dispute_status_enum", "dispute_type_enum",
        "late_fee_status_enum", "custody_event_type_enum", "deduction_type_enum",
        "deposit_status_enum", "payment_method_enum", "payment_status_enum",
        "invoice_status_enum", "quotation_status_enum", "extension_status_enum",
        "rental_type_enum", "rental_status_enum", "reservation_status_enum",
        "block_status_enum", "block_type_enum", "late_fee_mode_enum",
        "product_status_enum", "vote_choice_enum", "group_vote_status_enum",
        "group_vote_type_enum", "group_deposit_payment_status_enum",
        "group_deposit_status_enum", "group_member_status_enum",
        "group_member_role_enum", "group_status_enum",
        "enterprise_credit_txn_type_enum", "enterprise_kyc_status_enum",
        "enterprise_sub_role_enum", "legal_entity_type_enum",
        "kyc_record_status_enum", "otp_purpose_enum", "otp_channel_enum",
        "kyc_step_enum", "kyc_status_enum", "user_role_enum", "user_type_enum",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {e_name}")
