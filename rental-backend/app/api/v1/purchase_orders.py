# app/api/v1/purchase_orders.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.purchase_order import (
    PORequisitionCreate,
    PORequisitionResponse,
    PORequisitionListResponse,
    POReviewRequest,
    CreditRequestCreate,
)
from app.core.permissions import Permission
from app.services.purchase_order_service import PurchaseOrderService

router = APIRouter()


@router.get("/", response_model=PORequisitionListResponse)
async def list_purchase_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    enterprise_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = get_current_user,
):
    """List purchase orders with optional filters."""
    service = PurchaseOrderService(db)
    result = await service.list_pos(
        page=page,
        limit=limit,
        enterprise_id=enterprise_id,
        po_status=status,
    )
    return PORequisitionListResponse(**result)


@router.post("/", response_model=PORequisitionResponse, status_code=201)
async def create_purchase_order(
    data: PORequisitionCreate,
    enterprise_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = get_current_user,
):
    """Create a new purchase order requisition."""
    service = PurchaseOrderService(db)
    po = await service.create_po(
        data=data.model_dump(),
        enterprise_id=enterprise_id,
        requested_by=current_user.id,
    )
    return po


@router.get("/{po_id}", response_model=PORequisitionResponse)
async def get_purchase_order(
    po_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = get_current_user,
):
    """Get purchase order by ID."""
    service = PurchaseOrderService(db)
    return await service.get_po(po_id)


@router.post("/{po_id}/approve", response_model=PORequisitionResponse)
async def approve_purchase_order(
    po_id: uuid.UUID,
    data: POReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.ADMIN_DASHBOARD.value),
):
    """Approve a purchase order."""
    service = PurchaseOrderService(db)
    return await service.approve_po(
        po_id=po_id,
        reviewed_by=current_user.id,
        review_notes=data.review_notes,
    )


@router.post("/{po_id}/reject", response_model=PORequisitionResponse)
async def reject_purchase_order(
    po_id: uuid.UUID,
    data: POReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.ADMIN_DASHBOARD.value),
):
    """Reject a purchase order."""
    service = PurchaseOrderService(db)
    return await service.reject_po(
        po_id=po_id,
        reviewed_by=current_user.id,
        review_notes=data.review_notes,
    )
