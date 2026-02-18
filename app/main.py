"""FastAPI main application."""

import asyncio
import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from alembic.config import Config
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from alembic import command
from app.core.logging import setup_logging
from app.routers import tasks

# Get the project root directory (parent of app directory)
PROJECT_ROOT = Path(__file__).parent.parent

# Set up logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(level=log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Startup event."""
    logger.info("Starting up FastAPI application...")
    alembic_ini_path = PROJECT_ROOT / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini_path))
    await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
    logger.info("Database migrations applied successfully.")
    yield
    logger.info("Shutting down FastAPI application...")


app = FastAPI(title="FastAPI App", version="0.1.0", lifespan=lifespan)
app.include_router(tasks.router)


@app.get("/")
async def read_root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Hello, FastAPI!"}


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(status_code=200, content={"status": "ok"})


@app.get("/add")
async def add(x: int, y: int) -> dict[str, int]:
    """Add two integers."""
    return {"x": x, "y": y, "sum": x + y}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True,
    )
