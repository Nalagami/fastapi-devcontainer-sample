"""Integration test configuration."""

import pytest
from typing import AsyncGenerator, Generator

from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from app.main import app
from app.models.base import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def test_async_engine() -> AsyncEngine:
    """Create a test database engine."""
    return create_async_engine(
        TEST_DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
    )


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db(test_async_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Initialize test database."""
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_db_session(test_async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for tests."""
    async_session = async_sessionmaker(
        bind=test_async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True)
async def clean_db_before_test(test_async_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Clean data before each test."""
    # データをクリア（テーブル定義は保持）
    async with test_async_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield


@pytest.fixture
def client(test_db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Create a test client."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
