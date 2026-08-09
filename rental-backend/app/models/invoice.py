# app/models/invoice.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    RAZORPAY = "razorpay"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT = "credit"


class Invoice(BaseModel):
    __tablename__ = "invoices"

    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=True)
    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=True)
    status = Column(
        SAEnum(InvoiceStatus, name="invoice_status_enum", create_type=False),
        default=InvoiceStatus.DRAFT,
    )
    subtotal = Column(Numeric(12, 2), nullable=False)
    tax_amount = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    paid_amount = Column(Numeric(12, 2), default=0)
    due_date = Column(DateTime(timezone=True), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    billing_address = Column(JSONB, nullable=True)
    shipping_address = Column(JSONB, nullable=True)
    metadata_ = Column("metadata", JSONB, default={})

    # Relationships
    customer = relationship("User", foreign_keys=[customer_id])
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(BaseModel):
    __tablename__ = "invoice_items"

    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    metadata_ = Column("metadata", JSONB, default={})

    invoice = relationship("Invoice", back_populates="items")


class Payment(BaseModel):
    __tablename__ = "payments"

    payment_number = Column(String(50), unique=True, nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(
        SAEnum(PaymentStatus, name="payment_status_enum", create_type=False),
        default=PaymentStatus.PENDING,
    )
    payment_method = Column(
        SAEnum(PaymentMethod, name="payment_method_enum", create_type=False),
        nullable=False,
    )
    razorpay_order_id = Column(String(255), nullable=True)
    razorpay_payment_id = Column(String(255), nullable=True)
    razorpay_signature = Column(String(255), nullable=True)
    transaction_reference = Column(String(255), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    refund_amount = Column(Numeric(12, 2), nullable=True)
    refund_at = Column(DateTime(timezone=True), nullable=True)
    refund_reason = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, default={})

    invoice = relationship("Invoice", back_populates="payments")
    customer = relationship("User", foreign_keys=[customer_id])
