# app/api/v1/agent_tasks.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.agent_task import (
    AgentTaskCreate,
    AgentTaskUpdate,
    AgentTaskResponse,
    AgentTaskListResponse,
)
from app.core.permissions import Permission
from app.services.agent_task_service import AgentTaskService

router = APIRouter()


@router.get("/", response_model=AgentTaskListResponse)
async def list_agent_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    agent_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.INSPECTION_PERFORM.value),
):
    """List agent tasks with optional filters."""
    service = AgentTaskService(db)
    result = await service.list_tasks(
        page=page,
        limit=limit,
        agent_id=agent_id,
        task_status=status,
    )
    return AgentTaskListResponse(**result)


@router.post("/", response_model=AgentTaskResponse, status_code=201)
async def create_agent_task(
    data: AgentTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.INSPECTION_PERFORM.value),
):
    """Create a new agent task."""
    service = AgentTaskService(db)
    task = await service.create_task(data=data.model_dump())
    return task


@router.get("/{task_id}", response_model=AgentTaskResponse)
async def get_agent_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.INSPECTION_PERFORM.value),
):
    """Get agent task by ID."""
    service = AgentTaskService(db)
    return await service.get_task(task_id)


@router.put("/{task_id}", response_model=AgentTaskResponse)
async def update_agent_task(
    task_id: uuid.UUID,
    data: AgentTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.INSPECTION_PERFORM.value),
):
    """Update agent task details."""
    service = AgentTaskService(db)
    return await service.update_task(task_id, data.model_dump(exclude_unset=True))


@router.post("/{task_id}/start", response_model=AgentTaskResponse)
async def start_agent_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.INSPECTION_PERFORM.value),
):
    """Mark agent task as active/started."""
    service = AgentTaskService(db)
    return await service.start_task(task_id)


@router.post("/{task_id}/complete", response_model=AgentTaskResponse)
async def complete_agent_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.INSPECTION_PERFORM.value),
):
    """Mark agent task as completed."""
    service = AgentTaskService(db)
    return await service.complete_task(task_id)
