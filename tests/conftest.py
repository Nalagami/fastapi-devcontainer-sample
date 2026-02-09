"""Shared test configuration."""

from typing import Generator

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base


@pytest.fixture(scope="session")
def test_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def test_db_session(test_engine) -> Generator[Session, None, None]:
    """Create a new database session for each test."""
    connection = test_engine.connect()
    transaction = connection.begin()

    session = sessionmaker(bind=connection, expire_on_commit=False)()

    yield session

    session.rollback()
    session.close()
    transaction.rollback()
    connection.close()
