"""Pydantic schemas for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    """Schema for creating a task."""

    name: str
    deadline: datetime


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    name: str | None = None
    deadline: datetime | None = None
    is_completed: bool | None = None


class TaskResponse(BaseModel):
    """Schema for task response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    deadline: datetime
    is_completed: bool
