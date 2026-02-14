"""CRUD operations for Task model."""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


async def create_task(db: AsyncSession, name: str, deadline: datetime) -> Task:
    """Create a new task."""
    db_task = Task(name=name, deadline=deadline, is_completed=False)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def get_task(db: AsyncSession, task_id: int) -> Task | None:
    """Get a task by ID."""
    task = await db.execute(select(Task).where(Task.id == task_id))
    return task.scalar_one_or_none()


async def get_all_tasks(db: AsyncSession) -> Sequence[Task]:
    """Get all tasks."""
    tasks = await db.execute(select(Task))
    return tasks.scalars().all()


async def update_task(
    db: AsyncSession,
    task_id: int,
    name: str | None = None,
    deadline: datetime | None = None,
    is_completed: bool | None = None,
) -> Task | None:
    """Update a task."""
    task = await get_task(db=db, task_id=task_id)

    if task is None:
        return None

    if name is not None:
        task.name = name
    if deadline is not None:
        task.deadline = deadline
    if is_completed is not None:
        task.is_completed = is_completed

    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: int) -> None:
    """Delete a task."""
    task = await get_task(db=db, task_id=task_id)

    if task is not None:
        await db.delete(task)
        await db.commit()

    return None
