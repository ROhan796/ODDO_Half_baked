# app/api/v1/search.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.database import get_read_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/")
async def global_search(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Global search across products, rentals, invoices, and customers."""
    service = SearchService(db)
    return await service.global_search(query=q, limit=limit)
