# app/schemas/dashboard.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DashboardStats(BaseModel):
    total_rentals: int
    active_rentals: int
    pending_rentals: int
    overdue_rentals: int
    total_revenue: float
    monthly_revenue: float
    total_customers: int
    new_customers_today: int
    total_products: int
    available_products: int
    pending_invoices: int
    overdue_invoices: int


class RevenueChart(BaseModel):
    labels: List[str]
    values: List[float]


class RentalChart(BaseModel):
    labels: List[str]
    values: List[int]


class AdminDashboard(BaseModel):
    stats: DashboardStats
    revenue_chart: RevenueChart
    rental_chart: RentalChart
    recent_activity: List[dict]
    alerts: List[dict]
