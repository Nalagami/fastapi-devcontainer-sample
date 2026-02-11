from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task import create_task, delete_task, get_all_tasks, get_task, update_task
from app.models.base import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter()


@router.get("/tasks")
async def list_tasks(db: AsyncSession = Depends(get_db)) -> list[TaskResponse]:
    """Get all tasks."""
    tasks = await get_all_tasks(db=db)
    return [TaskResponse.model_validate(task) for task in tasks]


@router.post("/tasks", status_code=201)
async def create_new_task(task: TaskCreate, db: AsyncSession = Depends(get_db)) -> TaskResponse:
    """Create a new task."""
    db_task = await create_task(db=db, name=task.name, deadline=task.deadline)
    return TaskResponse.model_validate(db_task)


@router.get("/tasks/{task_id}")
async def get_single_task(task_id: int, db: AsyncSession = Depends(get_db)) -> TaskResponse:
    """Get a task by ID."""
    task = await get_task(db=db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.put("/tasks/{task_id}")
async def update_single_task(
    task_id: int, task_update: TaskUpdate, db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """Update a task."""
    updated_task = await update_task(
        db=db,
        task_id=task_id,
        name=task_update.name,
        deadline=task_update.deadline,
        is_completed=task_update.is_completed,
    )
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(updated_task)


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_single_task(task_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a task."""
    task = await get_task(db=db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await delete_task(db=db, task_id=task_id)
