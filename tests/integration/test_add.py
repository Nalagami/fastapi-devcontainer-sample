"""Test cases for add endpoint."""

from fastapi.testclient import TestClient


def test_add_integers(client: TestClient) -> None:
    """Test add endpoint with valid integers."""
    response = client.get("/add?x=5&y=3")
    assert response.status_code == 200
    data = response.json()
    assert data["x"] == 5
    assert data["y"] == 3
    assert data["sum"] == 8


def test_add_negative_integers(client: TestClient) -> None:
    """Test add endpoint with negative integers."""
    response = client.get("/add?x=-5&y=3")
    assert response.status_code == 200
    data = response.json()
    assert data["x"] == -5
    assert data["y"] == 3
    assert data["sum"] == -2


def test_add_zero(client: TestClient) -> None:
    """Test add endpoint with zero."""
    response = client.get("/add?x=0&y=0")
    assert response.status_code == 200
    data = response.json()
    assert data["x"] == 0
    assert data["y"] == 0
    assert data["sum"] == 0


def test_add_invalid_string(client: TestClient) -> None:
    """Test add endpoint with invalid string."""
    response = client.get("/add?x=abc&y=3")
    assert response.status_code == 422


def test_add_invalid_float(client: TestClient) -> None:
    """Test add endpoint with float."""
    response = client.get("/add?x=5.5&y=3")
    assert response.status_code == 422


def test_add_missing_parameter(client: TestClient) -> None:
    """Test add endpoint with missing parameter."""
    response = client.get("/add?x=5")
    assert response.status_code == 422
