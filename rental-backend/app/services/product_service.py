# app/services/product_service.py
from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.product import Product, ProductStatus


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, data: dict) -> Product:
        product = Product(**data)
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def get_product(self, product_id: UUID) -> Product:
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        return product

    async def list_products(
        self,
        page: int = 1,
        limit: int = 20,
        search: str = None,
        category_id: UUID = None,
        product_status: str = None,
    ) -> dict:
        query = select(Product)

        if search:
            search_filter = or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%"),
                Product.serial_number.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        if category_id:
            query = query.where(Product.category_id == category_id)

        if product_status:
            query = query.where(Product.status == product_status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        products = result.scalars().all()

        return {
            "items": products,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def update_product(self, product_id: UUID, data: dict) -> Product:
        product = await self.get_product(product_id)

        for key, value in data.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)

        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def delete_product(self, product_id: UUID) -> dict:
        product = await self.get_product(product_id)
        product.status = ProductStatus.ARCHIVED
        await self.db.flush()
        return {"message": "Product archived successfully"}
