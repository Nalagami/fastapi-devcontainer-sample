"""Integration test configuration."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.base import Base, async_engine


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db() -> None:
    """Initialize test database."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def clean_db_before_test() -> None:
    """Clean database before each test."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    return TestClient(app)
