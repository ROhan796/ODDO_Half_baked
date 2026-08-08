# app/core/permissions.py
from enum import Enum


class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    OPS_ADMIN = "ops_admin"
    FIELD_AGENT = "field_agent"
    PORTAL_USER = "portal_user"


class Permission(str, Enum):
    # Products
    PRODUCT_VIEW = "product:view"
    PRODUCT_CREATE = "product:create"
    PRODUCT_UPDATE = "product:update"
    PRODUCT_DELETE = "product:delete"

    # Rentals
    RENTAL_CREATE_OWN = "rental:create_own"
    RENTAL_CREATE_ANY = "rental:create_any"
    RENTAL_VIEW_OWN = "rental:view_own"
    RENTAL_VIEW_ANY = "rental:view_any"
    RENTAL_CONFIRM = "rental:confirm"
    RENTAL_RETURN = "rental:return"
    RENTAL_CANCEL = "rental:cancel"

    # Customers
    CUSTOMER_VIEW = "customer:view"
    CUSTOMER_CREATE = "customer:create"
    CUSTOMER_UPDATE = "customer:update"
    CUSTOMER_BLACKLIST = "customer:blacklist"

    # Finance
    DEPOSIT_VIEW = "deposit:view"
    DEPOSIT_SETTLE = "deposit:settle"
    DEPOSIT_DEDUCT = "deposit:deduct"
    INVOICE_VIEW = "invoice:view"
    INVOICE_CREATE = "invoice:create"

    # Operations
    INSPECTION_PERFORM = "inspection:perform"
    REPAIR_MANAGE = "repair:manage"
    RECOVERY_MANAGE = "recovery:manage"

    # Admin
    ADMIN_DASHBOARD = "admin:dashboard"
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_AUDIT = "admin:audit"
    ADMIN_BLACKLIST = "admin:blacklist"

    # CRM
    CRM_VIEW = "crm:view"
    CRM_MANAGE = "crm:manage"

    # Stock
    STOCK_VIEW = "stock:view"
    STOCK_MANAGE = "stock:manage"


# Permission matrix by role
ROLE_PERMISSIONS = {
    Role.SUPER_ADMIN: [p.value for p in Permission],
    Role.OPS_ADMIN: [
        Permission.PRODUCT_VIEW.value,
        Permission.PRODUCT_CREATE.value,
        Permission.PRODUCT_UPDATE.value,
        Permission.RENTAL_CREATE_ANY.value,
        Permission.RENTAL_VIEW_ANY.value,
        Permission.RENTAL_CONFIRM.value,
        Permission.RENTAL_RETURN.value,
        Permission.CUSTOMER_VIEW.value,
        Permission.CUSTOMER_CREATE.value,
        Permission.CUSTOMER_UPDATE.value,
        Permission.DEPOSIT_VIEW.value,
        Permission.DEPOSIT_SETTLE.value,
        Permission.DEPOSIT_DEDUCT.value,
        Permission.INVOICE_VIEW.value,
        Permission.INVOICE_CREATE.value,
        Permission.INSPECTION_PERFORM.value,
        Permission.REPAIR_MANAGE.value,
        Permission.ADMIN_DASHBOARD.value,
        Permission.ADMIN_AUDIT.value,
        Permission.CRM_VIEW.value,
        Permission.CRM_MANAGE.value,
        Permission.STOCK_VIEW.value,
        Permission.STOCK_MANAGE.value,
    ],
    Role.FIELD_AGENT: [
        Permission.PRODUCT_VIEW.value,
        Permission.RENTAL_VIEW_ANY.value,
        Permission.INSPECTION_PERFORM.value,
    ],
    Role.PORTAL_USER: [
        Permission.PRODUCT_VIEW.value,
        Permission.RENTAL_CREATE_OWN.value,
        Permission.RENTAL_VIEW_OWN.value,
        Permission.DEPOSIT_VIEW.value,
        Permission.INVOICE_VIEW.value,
    ],
}


def check_permission(role: str, permission: str) -> bool:
    """Check if role has specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, [])
