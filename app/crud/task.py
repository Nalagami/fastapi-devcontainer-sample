"""CRUD operations for Task model."""

from datetime import datetime

from app.models.base import SessionLocal
from app.models.task import Task


def create_task(name: str, deadline: datetime) -> Task:
    """Create a new task."""
    db = SessionLocal()
    db_task = Task(name=name, deadline=deadline, is_completed=False)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db.close()
    return db_task


def get_task(task_id: int) -> Task | None:
    """Get a task by ID."""
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    db.close()
    return task


def get_all_tasks() -> list[Task]:
    """Get all tasks."""
    db = SessionLocal()
    tasks = db.query(Task).all()
    db.close()
    return tasks


def update_task(
    task_id: int,
    name: str | None = None,
    deadline: datetime | None = None,
    is_completed: bool | None = None,
) -> Task | None:
    """Update a task."""
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        db.close()
        return None

    if name is not None:
        task.name = name
    if deadline is not None:
        task.deadline = deadline
    if is_completed is not None:
        task.is_completed = is_completed

    db.commit()
    db.refresh(task)
    db.close()
    return task


def delete_task(task_id: int) -> None:
    """Delete a task."""
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is not None:
        db.delete(task)
        db.commit()

    db.close()
