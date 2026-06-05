from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.qdrant import get_qdrant_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_qdrant_client()

    try:
        client.get_collections()
        print("Qdrant connected")
    except Exception as e:
        print(f"Qdrant connection failed: {e}")

    yield

    print("Shutting down...")


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