from fastapi import APIRouter, HTTPException

from app.crud.task import create_task, delete_task, get_all_tasks, get_task, update_task
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter()


@router.get("/tasks")
async def list_tasks() -> list[TaskResponse]:
    """Get all tasks."""
    tasks = get_all_tasks()
    return [TaskResponse.model_validate(task) for task in tasks]


@router.post("/tasks", status_code=201)
async def create_new_task(task: TaskCreate) -> TaskResponse:
    """Create a new task."""
    db_task = create_task(name=task.name, deadline=task.deadline)
    return TaskResponse.model_validate(db_task)


@router.get("/tasks/{task_id}")
async def get_single_task(task_id: int) -> TaskResponse:
    """Get a task by ID."""
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.put("/tasks/{task_id}")
async def update_single_task(task_id: int, task_update: TaskUpdate) -> TaskResponse:
    """Update a task."""
    updated_task = update_task(
        task_id,
        name=task_update.name,
        deadline=task_update.deadline,
        is_completed=task_update.is_completed,
    )
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(updated_task)


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_single_task(task_id: int) -> None:
    """Delete a task."""
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    delete_task(task_id)
