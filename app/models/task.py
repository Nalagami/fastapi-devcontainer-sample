"""SQLAlchemy Task model."""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Task(Base):
    """Task model for database."""

    __tablename__ = "tasks"

    id: Mapped[int | None] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    deadline: Mapped[datetime] = mapped_column(DateTime)
    is_completed: Mapped[bool] = mapped_column(default=False)
