# app/api/v1/admin.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid
from datetime import datetime, timezone

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.blacklist import Blacklist
from app.models.audit import AuditLog
from app.models.rental import Rental, RentalStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.product import Product, ProductStatus
from app.schemas.dashboard import DashboardStats, RevenueChart, RentalChart, AdminDashboard
from app.core.permissions import Permission

router = APIRouter()


@router.get("/dashboard")
async def get_admin_dashboard(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.ADMIN_DASHBOARD.value),
):
    """Get admin dashboard stats."""
    total_rentals = (await db.execute(select(func.count(Rental.id)))).scalar()
    active_rentals = (await db.execute(
        select(func.count(Rental.id)).where(Rental.status == RentalStatus.ACTIVE)
    )).scalar()
    pending_rentals = (await db.execute(
        select(func.count(Rental.id)).where(Rental.status == RentalStatus.PENDING)
    )).scalar()
    overdue_rentals = (await db.execute(
        select(func.count(Rental.id)).where(Rental.status == RentalStatus.OVERDUE)
    )).scalar()

    total_revenue = (await db.execute(
        select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(
            Invoice.status == InvoiceStatus.PAID
        )
    )).scalar()

    total_customers = (await db.execute(
        select(func.count(User.id)).where(User.role == "portal_user")
    )).scalar()

    total_products = (await db.execute(select(func.count(Product.id)))).scalar()
    available_products = (await db.execute(
        select(func.count(Product.id)).where(Product.status == ProductStatus.AVAILABLE)
    )).scalar()

    pending_invoices = (await db.execute(
        select(func.count(Invoice.id)).where(
            Invoice.status.in_([InvoiceStatus.PENDING, InvoiceStatus.PARTIALLY_PAID])
        )
    )).scalar()

    overdue_invoices = (await db.execute(
        select(func.count(Invoice.id)).where(Invoice.status == InvoiceStatus.OVERDUE)
    )).scalar()

    return DashboardStats(
        total_rentals=total_rentals or 0,
        active_rentals=active_rentals or 0,
        pending_rentals=pending_rentals or 0,
        overdue_rentals=overdue_rentals or 0,
        total_revenue=float(total_revenue or 0),
        monthly_revenue=float(total_revenue or 0),
        total_customers=total_customers or 0,
        new_customers_today=0,
        total_products=total_products or 0,
        available_products=available_products or 0,
        pending_invoices=pending_invoices or 0,
        overdue_invoices=overdue_invoices or 0,
    )


@router.get("/audit-logs")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[uuid.UUID] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.ADMIN_AUDIT.value),
):
    """List audit logs."""
    query = select(AuditLog)

    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    if action:
        query = query.where(AuditLog.action == action)

    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "items": logs,
        "total": total,
        "page": page,
        "limit": limit,
        "has_next": (page * limit) < total,
    }


@router.post("/blacklist")
async def blacklist_user(
    user_id: uuid.UUID,
    reason: str,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.ADMIN_BLACKLIST.value),
):
    """Blacklist a user."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot blacklist yourself")

    existing = await db.execute(
        select(Blacklist).where(Blacklist.user_id == user_id, Blacklist.removed_at.is_(None))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already blacklisted")

    now = datetime.now(timezone.utc)
    blacklist_entry = Blacklist(
        user_id=user_id,
        reason=reason,
        description=description,
        added_by=current_user.id,
        added_at=now,
    )
    db.add(blacklist_entry)

    user.blacklisted = True
    user.blacklisted_at = now
    user.blacklisted_by = current_user.id
    user.blacklist_reason = description or reason

    return {"message": "User blacklisted successfully"}


@router.delete("/blacklist/{user_id}")
async def remove_from_blacklist(
    user_id: uuid.UUID,
    removal_reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.ADMIN_BLACKLIST.value),
):
    """Remove user from blacklist."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(Blacklist).where(Blacklist.user_id == user_id, Blacklist.removed_at.is_(None))
    )
    blacklist_entry = result.scalar_one_or_none()
    if not blacklist_entry:
        raise HTTPException(status_code=404, detail="User is not blacklisted")

    now = datetime.now(timezone.utc)
    blacklist_entry.removed_by = current_user.id
    blacklist_entry.removed_at = now
    blacklist_entry.removal_reason = removal_reason

    user.blacklisted = False
    user.blacklisted_at = None
    user.blacklisted_by = None
    user.blacklist_reason = None

    return {"message": "User removed from blacklist"}


@router.get("/blacklist")
async def list_blacklisted_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.ADMIN_BLACKLIST.value),
):
    """List blacklisted users."""
    query = select(Blacklist).where(Blacklist.removed_at.is_(None))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.order_by(Blacklist.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    entries = result.scalars().all()

    return {
        "items": entries,
        "total": total,
        "page": page,
        "limit": limit,
        "has_next": (page * limit) < total,
    }


@router.get("/system/health")
async def system_health_check(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.ADMIN_DASHBOARD.value),
):
    """Detailed system health check."""
    health_status = {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        await db.execute(select(func.count(User.id)))
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["database"] = f"error: {str(e)}"

    return health_status
