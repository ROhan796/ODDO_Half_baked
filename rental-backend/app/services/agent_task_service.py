# app/services/agent_task_service.py
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.agent_task import AgentTask, Agent, TaskStatus


class AgentTaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, data: dict) -> AgentTask:
        task = AgentTask(**data)
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def get_task(self, task_id: UUID) -> AgentTask:
        result = await self.db.execute(
            select(AgentTask).where(AgentTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent task not found",
            )
        return task

    async def list_tasks(
        self,
        page: int = 1,
        limit: int = 20,
        agent_id: UUID = None,
        task_status: str = None,
    ) -> dict:
        query = select(AgentTask)

        if agent_id:
            query = query.where(AgentTask.agent_id == agent_id)

        if task_status:
            query = query.where(AgentTask.status == task_status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(AgentTask.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return {
            "items": tasks,
            "total": total,
            "page": page,
            "limit": limit,
            "has_next": (page * limit) < total,
        }

    async def update_task(self, task_id: UUID, data: dict) -> AgentTask:
        task = await self.get_task(task_id)

        for key, value in data.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def start_task(self, task_id: UUID) -> AgentTask:
        task = await self.get_task(task_id)

        if task.status not in (TaskStatus.PENDING, TaskStatus.CONFIRMED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start task in {task.status.value} status",
            )

        task.status = TaskStatus.ACTIVE
        task.started_at = datetime.now(timezone.utc)

        if task.agent_id:
            agent = await self.db.get(Agent, task.agent_id)
            if agent:
                agent.active_task_id = task.id
                agent.status = "on_task"

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def complete_task(self, task_id: UUID) -> AgentTask:
        task = await self.get_task(task_id)

        if task.status != TaskStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete task in {task.status.value} status",
            )

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(timezone.utc)

        if task.agent_id:
            agent = await self.db.get(Agent, task.agent_id)
            if agent:
                agent.active_task_id = None
                agent.status = "online"

        await self.db.flush()
        await self.db.refresh(task)
        return task


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_agent(self, data: dict) -> Agent:
        agent = Agent(**data)
        self.db.add(agent)
        await self.db.flush()
        await self.db.refresh(agent)
        return agent

    async def get_agent(self, agent_id: UUID) -> Agent:
        result = await self.db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found",
            )
        return agent

    async def get_agent_by_user(self, user_id: UUID) -> Agent:
        result = await self.db.execute(
            select(Agent).where(Agent.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_agents(self) -> list:
        result = await self.db.execute(select(Agent))
        return result.scalars().all()
