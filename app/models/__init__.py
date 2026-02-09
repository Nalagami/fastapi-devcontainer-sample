"""SQLAlchemy models for the application."""

from app.models.base import Base, SessionLocal, engine  # noqa: F401
from app.models.task import Task  # noqa: F401

# Create tables
Base.metadata.create_all(bind=engine)
