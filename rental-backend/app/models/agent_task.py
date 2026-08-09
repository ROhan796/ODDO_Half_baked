# app/models/agent_task.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class TaskType(str, enum.Enum):
    DELIVERY = "delivery"
    PICKUP = "pickup"
    INSPECTION = "inspection"
    RETURN = "return"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    OVERDUE = "overdue"
    COMPLETED = "completed"


class AgentStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ON_TASK = "on_task"


class Agent(BaseModel):
    __tablename__ = "agents"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    status = Column(
        SAEnum(AgentStatus, name="agent_status_enum"),
        default=AgentStatus.OFFLINE,
    )
    location_hub = Column(String(255), nullable=True)
    active_task_id = Column(UUID(as_uuid=True), ForeignKey("agent_tasks.id"), nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    active_task = relationship("AgentTask", foreign_keys=[active_task_id], post_update=True)
    tasks = relationship("AgentTask", back_populates="agent", foreign_keys="AgentTask.agent_id")


class AgentTask(BaseModel):
    __tablename__ = "agent_tasks"

    rental_id = Column(UUID(as_uuid=True), ForeignKey("rentals.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    task_type = Column(
        SAEnum(TaskType, name="agent_task_type_enum"),
        nullable=False,
    )
    status = Column(
        SAEnum(TaskStatus, name="agent_task_status_enum"),
        default=TaskStatus.PENDING,
    )
    address = Column(Text, nullable=True)
    customer_name = Column(String(255), nullable=True)
    customer_phone = Column(String(15), nullable=True)
    product_name = Column(String(255), nullable=True)
    gps_lat = Column(Numeric(10, 8), nullable=True)
    gps_lng = Column(Numeric(11, 8), nullable=True)
    notes = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    rental = relationship("Rental", foreign_keys=[rental_id])
    agent = relationship("Agent", back_populates="tasks", foreign_keys=[agent_id])
