"""add software services tables

Revision ID: 002
Revises: 001
Create Date: 2026-08-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    license_type_enum = postgresql.ENUM(
        "saas_subscription", "node_locked", "floating", "cloud_credit", "api_quota",
        name="license_type_enum", create_type=False,
    )
    software_delivery_method_enum = postgresql.ENUM(
        "email_license_key", "cloud_access", "api_key", "download_link",
        name="software_delivery_method_enum", create_type=False,
    )
    software_service_status_enum = postgresql.ENUM(
        "available", "rented", "deprecated", "inactive",
        name="software_service_status_enum", create_type=False,
    )
    software_rental_status_enum = postgresql.ENUM(
        "pending", "active", "suspended", "expired", "cancelled",
        name="software_rental_status_enum", create_type=False,
    )

    # Create enums if they don't exist
    for enum in [license_type_enum, software_delivery_method_enum, software_service_status_enum, software_rental_status_enum]:
        try:
            enum.create(op.get_bind(), checkfirst=True)
        except Exception:
            pass

    # Create software_services table
    op.create_table(
        "software_services",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("short_description", sa.String(500), nullable=True),
        sa.Column("vendor", sa.String(255), nullable=True),
        sa.Column("version", sa.String(50), nullable=True),
        sa.Column("license_type", license_type_enum, nullable=False),
        sa.Column("delivery_method", software_delivery_method_enum, nullable=False),
        sa.Column("hourly_rate", sa.Numeric(10, 2), nullable=True),
        sa.Column("daily_rate", sa.Numeric(10, 2), nullable=True),
        sa.Column("weekly_rate", sa.Numeric(10, 2), nullable=True),
        sa.Column("monthly_rate", sa.Numeric(10, 2), nullable=True),
        sa.Column("annual_rate", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(3), server_default="INR"),
        sa.Column("max_concurrent_users", sa.Integer, server_default="1"),
        sa.Column("max_seats", sa.Integer, nullable=True),
        sa.Column("requires_vpn", sa.Boolean, server_default="false"),
        sa.Column("ip_whitelist", postgresql.ARRAY(sa.Text), server_default="{}"),
        sa.Column("system_requirements", sa.Text, nullable=True),
        sa.Column("api_endpoint", sa.Text, nullable=True),
        sa.Column("documentation_url", sa.Text, nullable=True),
        sa.Column("support_email", sa.String(255), nullable=True),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("tags", postgresql.ARRAY(sa.Text), server_default="{}"),
        sa.Column("images", postgresql.ARRAY(sa.Text), server_default="{}"),
        sa.Column("thumbnail_url", sa.Text, nullable=True),
        sa.Column("status", software_service_status_enum, server_default="available"),
        sa.Column("is_featured", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create software_rentals table
    op.create_table(
        "software_rentals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("rental_number", sa.String(20), unique=True, nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("software_service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("software_services.id"), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual_access_revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("license_key", sa.Text, nullable=True),
        sa.Column("license_server_url", sa.Text, nullable=True),
        sa.Column("api_key_hash", sa.String(255), nullable=True),
        sa.Column("access_credentials", postgresql.JSONB, nullable=True),
        sa.Column("rental_fee", sa.Numeric(12, 2), nullable=False),
        sa.Column("security_deposit_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("currency", sa.String(3), server_default="INR"),
        sa.Column("usage_metric", sa.String(50), nullable=True),
        sa.Column("usage_limit", sa.Numeric(12, 2), nullable=True),
        sa.Column("usage_current", sa.Numeric(12, 2), server_default="0"),
        sa.Column("status", software_rental_status_enum, server_default="pending"),
        sa.Column("provisioned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("access_granted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("access_revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("quotation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quotations.id"), nullable=True),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("invoices.id"), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create software_usage_logs table
    op.create_table(
        "software_usage_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("software_rental_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("software_rentals.id"), nullable=False),
        sa.Column("metric_type", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create indexes
    op.create_index("idx_software_services_slug", "software_services", ["slug"], unique=True)
    op.create_index("idx_software_services_category", "software_services", ["category_id"])
    op.create_index("idx_software_services_status", "software_services", ["status"])
    op.create_index("idx_software_services_license_type", "software_services", ["license_type"])
    op.create_index("idx_software_rentals_customer", "software_rentals", ["customer_id"])
    op.create_index("idx_software_rentals_service", "software_rentals", ["software_service_id"])
    op.create_index("idx_software_rentals_status", "software_rentals", ["status"])
    op.create_index("idx_software_rentals_number", "software_rentals", ["rental_number"], unique=True)
    op.create_index("idx_software_usage_rental", "software_usage_logs", ["software_rental_id"])
    op.create_index("idx_software_usage_timestamp", "software_usage_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("software_usage_logs")
    op.drop_table("software_rentals")
    op.drop_table("software_services")

    # Drop enums
    for enum_name in [
        "software_rental_status_enum",
        "software_service_status_enum",
        "software_delivery_method_enum",
        "license_type_enum",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
