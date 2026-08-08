# app/api/v1/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from typing import Optional
import uuid
from datetime import datetime, timedelta, timezone

from app.utils.database import get_read_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.rental import Rental, RentalStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.product import Product, ProductStatus
from app.schemas.dashboard import DashboardStats, RevenueChart, RentalChart, AdminDashboard
from app.core.permissions import Permission

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard statistics."""
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

    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = (await db.execute(
        select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(
            Invoice.status == InvoiceStatus.PAID,
            Invoice.created_at >= month_start,
        )
    )).scalar()

    total_customers = (await db.execute(
        select(func.count(User.id)).where(User.role == "portal_user")
    )).scalar()

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    new_customers_today = (await db.execute(
        select(func.count(User.id)).where(
            User.role == "portal_user",
            User.created_at >= today_start,
        )
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
        monthly_revenue=float(monthly_revenue or 0),
        total_customers=total_customers or 0,
        new_customers_today=new_customers_today or 0,
        total_products=total_products or 0,
        available_products=available_products or 0,
        pending_invoices=pending_invoices or 0,
        overdue_invoices=overdue_invoices or 0,
    )


@router.get("/revenue-chart", response_model=RevenueChart)
async def get_revenue_chart(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get revenue chart data for the last 30 days."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    labels = []
    values = []

    for i in range(30):
        day = thirty_days_ago + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        result = await db.execute(
            select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(
                Invoice.status == InvoiceStatus.PAID,
                Invoice.created_at >= day_start,
                Invoice.created_at < day_end,
            )
        )
        revenue = result.scalar()
        labels.append(day.strftime("%b %d"))
        values.append(float(revenue or 0))

    return RevenueChart(labels=labels, values=values)


@router.get("/rental-chart", response_model=RentalChart)
async def get_rental_chart(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get rental chart data for the last 30 days."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    labels = []
    values = []

    for i in range(30):
        day = thirty_days_ago + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        result = await db.execute(
            select(func.count(Rental.id)).where(
                Rental.created_at >= day_start,
                Rental.created_at < day_end,
            )
        )
        count = result.scalar()
        labels.append(day.strftime("%b %d"))
        values.append(count or 0)

    return RentalChart(labels=labels, values=values)
