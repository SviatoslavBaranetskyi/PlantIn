from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    lifespan=lifespan,
)


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}