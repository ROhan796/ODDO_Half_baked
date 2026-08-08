# app/api/v1/products.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.core.permissions import Permission

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_read_db),
):
    """List all products."""
    query = select(Product)

    if search:
        query = query.where(
            (Product.name.ilike(f"%{search}%"))
            | (Product.description.ilike(f"%{search}%"))
        )

    if category_id:
        query = query.where(Product.category_id == category_id)

    if status:
        query = query.where(Product.status == status)

    # Get total count
    from sqlalchemy import func

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()

    return ProductListResponse(
        items=products,
        total=total,
        page=page,
        limit=limit,
        has_next=(page * limit) < total,
    )


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.PRODUCT_CREATE.value),
):
    """Create a new product."""
    product = Product(**data.model_dump())
    db.add(product)
    return product


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
):
    """Get product by ID."""
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.PRODUCT_UPDATE.value),
):
    """Update product."""
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.PRODUCT_DELETE.value),
):
    """Delete product."""
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(product)
    return {"message": "Product deleted successfully"}
