# app/core/events.py
from enum import Enum


class WSEvent(str, Enum):
    # Connection events
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"

    # Rental events
    RENTAL_CREATED = "rental:created"
    RENTAL_UPDATED = "rental:updated"
    RENTAL_RETURNED = "rental:returned"
    RENTAL_EXTENDED = "rental:extended"

    # Payment events
    PAYMENT_RECEIVED = "payment:received"
    PAYMENT_FAILED = "payment:failed"
    INVOICE_GENERATED = "invoice:generated"

    # Stock events
    STOCK_LOW = "stock:low"
    STOCK_UPDATED = "stock:updated"
    PRODUCT_AVAILABLE = "product:available"

    # Notification events
    NOTIFICATION_NEW = "notification:new"
    NOTIFICATION_READ = "notification:read"

    # CRM events
    CRM_FOLLOW_UP = "crm:follow_up"
    CRM_INTERACTION = "crm:interaction"

    # System events
    SYSTEM_MAINTENANCE = "system:maintenance"
    SYSTEM_ALERT = "system:alert"
