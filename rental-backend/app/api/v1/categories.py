# app/api/v1/categories.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.product import Category
from app.schemas.product import CategoryCreate, CategoryResponse
from app.core.permissions import Permission

router = APIRouter()


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_read_db)):
    """List all categories."""
    result = await db.execute(select(Category).where(Category.is_active == True))
    return result.scalars().all()


@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.PRODUCT_CREATE.value),
):
    """Create a new category."""
    category = Category(**data.model_dump())
    db.add(category)
    return category


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    db: AsyncSession = Depends(get_read_db),
):
    """Get category by ID."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
