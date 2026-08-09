# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1 import (
    auth,
    users,
    products,
    categories,
    rentals,
    quotations,
    invoices,
    deposits,
    disputes,
    repairs,
    recovery,
    groups,
    enterprise,
    crm,
    stock,
    loyalty,
    notifications,
    admin,
    files,
    dashboard,
    software_services,
    software_rentals,
    agent_tasks,
    inspections,
    purchase_orders,
    addresses,
    search,
    departments,
    custody,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(rentals.router, prefix="/rentals", tags=["Rentals"])
api_router.include_router(quotations.router, prefix="/quotations", tags=["Quotations"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
api_router.include_router(deposits.router, prefix="/deposits", tags=["Deposits"])
api_router.include_router(disputes.router, prefix="/disputes", tags=["Disputes"])
api_router.include_router(repairs.router, prefix="/repairs", tags=["Repairs"])
api_router.include_router(recovery.router, prefix="/recovery", tags=["Recovery"])
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
api_router.include_router(enterprise.router, prefix="/enterprise", tags=["Enterprise"])
api_router.include_router(crm.router, prefix="/crm", tags=["CRM"])
api_router.include_router(stock.router, prefix="/stock", tags=["Stock"])
api_router.include_router(loyalty.router, prefix="/loyalty", tags=["Loyalty"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(software_services.router, prefix="/software-services", tags=["Software Services"])
api_router.include_router(software_rentals.router, prefix="/software-rentals", tags=["Software Rentals"])
api_router.include_router(agent_tasks.router, prefix="/agent-tasks", tags=["Agent Tasks"])
api_router.include_router(inspections.router, prefix="/inspections", tags=["Inspections"])
api_router.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["Purchase Orders"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["Addresses"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])
api_router.include_router(custody.router, prefix="/custody", tags=["Custody"])
