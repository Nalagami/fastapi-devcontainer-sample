"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.routers import tasks

app = FastAPI(title="FastAPI App", version="0.1.0")
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
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
