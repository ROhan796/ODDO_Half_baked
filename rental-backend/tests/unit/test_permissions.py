"""Unit tests for permission system."""
import pytest
from app.core.permissions import (
    Role,
    Permission,
    ROLE_PERMISSIONS,
    check_permission,
)


class TestRolePermissions:
    def test_super_admin_has_all_permissions(self):
        super_admin_perms = ROLE_PERMISSIONS[Role.SUPER_ADMIN]
        all_perms = [p.value for p in Permission]
        assert set(all_perms).issubset(set(super_admin_perms))

    def test_portal_user_has_limited_permissions(self):
        portal_perms = ROLE_PERMISSIONS[Role.PORTAL_USER]
        assert Permission.PRODUCT_VIEW.value in portal_perms
        assert Permission.RENTAL_CREATE_OWN.value in portal_perms
        assert Permission.RENTAL_VIEW_OWN.value in portal_perms
        assert Permission.DEPOSIT_VIEW.value in portal_perms
        assert Permission.INVOICE_VIEW.value in portal_perms
        # Should NOT have admin permissions
        assert Permission.ADMIN_DASHBOARD.value not in portal_perms
        assert Permission.ADMIN_SETTINGS.value not in portal_perms
        assert Permission.RENTAL_CREATE_ANY.value not in portal_perms

    def test_ops_admin_has_operational_permissions(self):
        ops_perms = ROLE_PERMISSIONS[Role.OPS_ADMIN]
        assert Permission.PRODUCT_CREATE.value in ops_perms
        assert Permission.RENTAL_CREATE_ANY.value in ops_perms
        assert Permission.RENTAL_CONFIRM.value in ops_perms
        assert Permission.ADMIN_DASHBOARD.value in ops_perms
        assert Permission.STOCK_MANAGE.value in ops_perms

    def test_field_agent_has_minimal_permissions(self):
        field_perms = ROLE_PERMISSIONS[Role.FIELD_AGENT]
        assert Permission.PRODUCT_VIEW.value in field_perms
        assert Permission.RENTAL_VIEW_ANY.value in field_perms
        assert Permission.INSPECTION_PERFORM.value in field_perms
        assert len(field_perms) == 3

    def test_all_roles_are_defined(self):
        assert Role.SUPER_ADMIN.value == "super_admin"
        assert Role.OPS_ADMIN.value == "ops_admin"
        assert Role.FIELD_AGENT.value == "field_agent"
        assert Role.PORTAL_USER.value == "portal_user"


class TestCheckPermission:
    def test_super_admin_check_permission(self):
        assert check_permission("super_admin", "product:view") is True
        assert check_permission("super_admin", "admin:settings") is True
        assert check_permission("super_admin", "rental:create_own") is True

    def test_portal_user_check_permission(self):
        assert check_permission("portal_user", "product:view") is True
        assert check_permission("portal_user", "rental:create_own") is True
        assert check_permission("portal_user", "admin:settings") is False
        assert check_permission("portal_user", "rental:create_any") is False

    def test_check_permission_unknown_role(self):
        assert check_permission("unknown_role", "product:view") is False

    def test_check_permission_invalid_permission(self):
        assert check_permission("super_admin", "nonexistent:permission") is False

    def test_check_permission_ops_admin(self):
        assert check_permission("ops_admin", "rental:confirm") is True
        assert check_permission("ops_admin", "repair:manage") is True
        assert check_permission("ops_admin", "admin:settings") is False

    def test_check_permission_field_agent(self):
        assert check_permission("field_agent", "inspection:perform") is True
        assert check_permission("field_agent", "product:create") is False
