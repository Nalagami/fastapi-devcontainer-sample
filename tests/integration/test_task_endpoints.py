"""Integration tests for Task API endpoints."""

from datetime import datetime

from fastapi.testclient import TestClient


def test_get_all_tasks(client: TestClient) -> None:
    """Test GET /tasks endpoint."""
    response = client.get("/tasks")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_task(client: TestClient) -> None:
    """Test POST /tasks endpoint."""
    task_data = {
        "name": "New task",
        "deadline": "2024-12-31T23:59:59",
    }

    response = client.post("/tasks", json=task_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New task"
    assert data["is_completed"] is False
    assert "id" in data


def test_get_task_by_id(client: TestClient) -> None:
    """Test GET /tasks/{id} endpoint."""
    # Create a task first
    task_data = {
        "name": "Test task",
        "deadline": "2024-12-31T23:59:59",
    }
    create_response = client.post("/tasks", json=task_data)
    task_id = create_response.json()["id"]

    # Get the task
    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["name"] == "Test task"


def test_get_task_not_found(client: TestClient) -> None:
    """Test GET /tasks/{id} with non-existent ID."""
    response = client.get("/tasks/999")

    assert response.status_code == 404


def test_update_task(client: TestClient) -> None:
    """Test PUT /tasks/{id} endpoint."""
    # Create a task first
    task_data = {
        "name": "Original name",
        "deadline": "2024-12-31T23:59:59",
    }
    create_response = client.post("/tasks", json=task_data)
    task_id = create_response.json()["id"]

    # Update the task
    update_data = {
        "name": "Updated name",
        "is_completed": True,
    }
    response = client.put(f"/tasks/{task_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated name"
    assert data["is_completed"] is True


def test_update_task_not_found(client: TestClient) -> None:
    """Test PUT /tasks/{id} with non-existent ID."""
    update_data = {
        "name": "New name",
    }
    response = client.put("/tasks/999", json=update_data)

    assert response.status_code == 404


def test_delete_task(client: TestClient) -> None:
    """Test DELETE /tasks/{id} endpoint."""
    # Create a task first
    task_data = {
        "name": "To delete",
        "deadline": "2024-12-31T23:59:59",
    }
    create_response = client.post("/tasks", json=task_data)
    task_id = create_response.json()["id"]

    # Delete the task
    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_task_not_found(client: TestClient) -> None:
    """Test DELETE /tasks/{id} with non-existent ID."""
    response = client.delete("/tasks/999")

    assert response.status_code == 404
