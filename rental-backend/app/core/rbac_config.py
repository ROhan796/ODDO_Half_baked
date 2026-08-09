# app/core/rbac_config.py
"""
RBAC Configuration — Email-to-Role Mapping

This file defines which email addresses get which roles.
Used by:
1. Clerk webhook (auto-assigns role on user.created)
2. Seed script (backfills roles for existing users)
3. Frontend (renders pages based on role)
"""
from app.core.permissions import Role


# ============================================
# USER-ROLE MAPPING (add your team emails here)
# ============================================
USER_ROLE_MAP: dict[str, str] = {
    # Super Admin — full access to everything
    "jetp292@gmail.com": Role.SUPER_ADMIN,
    "admin@rental.com": Role.SUPER_ADMIN,

    # Ops Admin — manage properties, tenants, operations
    "rmxdeath@gmail.com": Role.OPS_ADMIN,
    "mannarohan@gmail.com": Role.OPS_ADMIN,
    "admin@reprico.com": Role.OPS_ADMIN,

    # Field Agent — view-only, inspections, limited ops
    "rohanmannas2021@gmail.com": Role.FIELD_AGENT,
    "suresh.agent@reprico.com": Role.FIELD_AGENT,

    # Portal User — customer-facing, own data only
    "roix107@gmail.com": Role.PORTAL_USER,
    "rahul.sharma@example.com": Role.PORTAL_USER,
    "priya.nair@nexusmedia.in": Role.PORTAL_USER,
    "arjun@indiecreatives.org": Role.PORTAL_USER,
}


def get_role_for_email(email: str) -> str | None:
    """Look up the role for a given email address."""
    return USER_ROLE_MAP.get(email.lower().strip())


# ============================================
# ROLE DISPLAY NAMES (for frontend)
# ============================================
ROLE_DISPLAY_NAMES: dict[str, str] = {
    Role.SUPER_ADMIN: "Super Admin",
    Role.OPS_ADMIN: "Operations Admin",
    Role.FIELD_AGENT: "Field Agent",
    Role.PORTAL_USER: "Customer",
}


# ============================================
# ROLE PORTAL ACCESS (which portals each role can access)
# ============================================
ROLE_PORTALS: dict[str, list[str]] = {
    Role.SUPER_ADMIN: ["admin", "ops", "field", "customer"],
    Role.OPS_ADMIN: ["ops", "field"],
    Role.FIELD_AGENT: ["field"],
    Role.PORTAL_USER: ["customer"],
}
