import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.duplicates import router as duplicates_router
from app.api.routes.images import router as images_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.qdrant import get_qdrant_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_qdrant_client()

    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        client.get_collections()
        logger.info("Qdrant connected")
    except Exception as e:
        logger.exception(f"Qdrant connection failed: {e}")

    yield

    logger.info("Shutting down...")


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


app.include_router(images_router)
app.include_router(duplicates_router)
