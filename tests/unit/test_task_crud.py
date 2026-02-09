"""Unit tests for Task CRUD operations."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.task import Task


def test_create_task() -> None:
    """Test creating a task in the database."""
    from app.crud.task import create_task

    deadline = datetime(2024, 12, 31, 23, 59, 59)
    task = create_task(name="Complete report", deadline=deadline)

    assert task.id is not None
    assert task.name == "Complete report"
    assert task.deadline == deadline
    assert task.is_completed is False


def test_get_task_by_id(test_db_session: Session) -> None:
    """Test retrieving a task by ID."""
    from app.crud.task import get_task

    deadline = datetime(2024, 12, 31, 23, 59, 59)
    task = Task(name="Test task", deadline=deadline, is_completed=False)
    test_db_session.add(task)
    test_db_session.commit()

    retrieved_task = get_task(task.id)

    assert retrieved_task is not None
    assert retrieved_task.id == task.id
    assert retrieved_task.name == "Test task"


def test_get_task_not_found() -> None:
    """Test getting a task that doesn't exist."""
    from app.crud.task import get_task

    result = get_task(999)

    assert result is None


def test_get_all_tasks(test_db_session: Session) -> None:
    """Test retrieving all tasks."""
    from app.crud.task import get_all_tasks

    deadline = datetime(2024, 12, 31, 23, 59, 59)
    task1 = Task(name="Task 1", deadline=deadline, is_completed=False, id=1)
    task2 = Task(name="Task 2", deadline=deadline, is_completed=False, id=2)
    test_db_session.add(task1)
    test_db_session.add(task2)
    test_db_session.commit()

    tasks = get_all_tasks()

    assert len(tasks) == 2
    assert any(task.name == "Task 1" for task in tasks)
    assert any(task.name == "Task 2" for task in tasks)


def test_update_task(test_db_session: Session) -> None:
    """Test updating a task."""
    from app.crud.task import update_task

    deadline = datetime(2024, 12, 31, 23, 59, 59)
    task = Task(name="Original name", deadline=deadline, is_completed=False)
    test_db_session.add(task)
    test_db_session.commit()

    updated_task = update_task(task.id, name="Updated name", is_completed=True)

    assert updated_task is not None
    assert updated_task.id == task.id
    assert updated_task.name == "Updated name"
    assert updated_task.is_completed is True


def test_update_task_not_found() -> None:
    """Test updating a task that doesn't exist."""
    from app.crud.task import update_task

    result = update_task(999, name="New name")

    assert result is None


def test_delete_task(test_db_session: Session) -> None:
    """Test deleting a task."""
    from app.crud.task import delete_task, get_task

    deadline = datetime(2024, 12, 31, 23, 59, 59)
    task = Task(name="To delete", deadline=deadline, is_completed=False)
    test_db_session.add(task)
    test_db_session.commit()
    task_id = task.id

    delete_task(task_id)
    result = get_task(task_id)

    assert result is None


def test_delete_task_not_found() -> None:
    """Test deleting a task that doesn't exist."""
    from app.crud.task import delete_task

    # Should not raise an error
    delete_task(999)
