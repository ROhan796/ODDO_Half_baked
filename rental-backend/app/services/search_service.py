# app/services/search_service.py
from uuid import UUID
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.rental import Rental
from app.models.invoice import Invoice
from app.models.user import User


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def global_search(self, query: str, limit: int = 20) -> dict:
        search_term = f"%{query}%"

        product_query = (
            select(Product)
            .where(
                or_(
                    Product.name.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Product.serial_number.ilike(search_term),
                    Product.description.ilike(search_term),
                )
            )
            .limit(10)
        )
        products_result = await self.db.execute(product_query)
        products = [
            {
                "type": "product",
                "id": str(p.id),
                "title": p.name,
                "subtitle": p.sku or p.serial_number or "",
                "status": p.status.value if hasattr(p.status, 'value') else p.status,
            }
            for p in products_result.scalars().all()
        ]

        rental_query = (
            select(Rental)
            .where(
                or_(
                    Rental.id.cast(str).ilike(search_term),
                    Rental.status.ilike(search_term),
                )
            )
            .limit(10)
        )
        rentals_result = await self.db.execute(rental_query)
        rentals = [
            {
                "type": "rental",
                "id": str(r.id),
                "title": f"Rental #{str(r.id)[:8]}",
                "subtitle": r.status.value if hasattr(r.status, 'value') else r.status,
                "status": r.status.value if hasattr(r.status, 'value') else r.status,
            }
            for r in rentals_result.scalars().all()
        ]

        invoice_query = (
            select(Invoice)
            .where(
                or_(
                    Invoice.id.cast(str).ilike(search_term),
                    Invoice.invoice_number.ilike(search_term) if hasattr(Invoice, 'invoice_number') else Invoice.id.cast(str).ilike(search_term),
                )
            )
            .limit(10)
        )
        invoices_result = await self.db.execute(invoice_query)
        invoices = [
            {
                "type": "invoice",
                "id": str(i.id),
                "title": f"Invoice #{str(i.id)[:8]}",
                "subtitle": i.status if hasattr(i, 'status') else "",
                "status": i.status if hasattr(i, 'status') else "",
            }
            for i in invoices_result.scalars().all()
        ]

        customer_query = (
            select(User)
            .where(
                or_(
                    User.name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.phone.ilike(search_term),
                )
            )
            .limit(10)
        )
        customers_result = await self.db.execute(customer_query)
        customers = [
            {
                "type": "customer",
                "id": str(c.id),
                "title": c.name,
                "subtitle": c.email,
                "status": c.kyc_status.value if hasattr(c.kyc_status, 'value') else str(c.kyc_status),
            }
            for c in customers_result.scalars().all()
        ]

        all_results = products + rentals + invoices + customers
        return {
            "query": query,
            "results": all_results[:limit],
            "total": len(all_results),
        }
