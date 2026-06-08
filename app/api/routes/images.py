import logging
from functools import lru_cache
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.db.qdrant import get_qdrant_client
from app.models.responses import UploadImagesResponse
from app.repositories.request_repository import RequestRepository
from app.services.embedding_service import EmbeddingService
from app.services.image_processor import ImageProcessor
from app.services.vector_store import VectorStore

logger = logging.getLogger(__name__)

router = APIRouter()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


@router.post("/images", response_model=UploadImagesResponse)
async def upload_images(files: Annotated[list[UploadFile], File()]):
    logger.info(
        "Upload request received with %s files",
        len(files),
    )

    if not files:
        raise HTTPException(status_code=400, detail="At least one image is required")

    image_processor = ImageProcessor(settings.max_image_size_mb)
    repo = RequestRepository()
    request_id = str(uuid4())
    prepared_images = []

    for file in files:
        file_bytes = await file.read()

        try:
            image_processor.validate_image(file_bytes)
            image = image_processor.load_image(file_bytes)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        prepared_images.append((file.filename, image_processor.preprocess(image)))

    embedding_service = get_embedding_service()
    vector_store = VectorStore(get_qdrant_client())
    image_ids = []
    points = []

    for filename, image in prepared_images:
        image_id = str(uuid4())
        embedding = embedding_service.encode(image)

        points.append(
            {
                "id": image_id,
                "vector": embedding,
                "payload": {
                    "filename": filename,
                    "request_id": request_id,
                },
            }
        )

        image_ids.append(image_id)

    vector_store.upsert_embeddings(points)
    repo.create_request(image_ids, request_id=request_id)

    logger.info(
        "Upload request completed: request_id=%s uploaded=%s",
        request_id,
        len(image_ids),
    )

    return UploadImagesResponse(
        request_id=request_id,
        uploaded=len(image_ids),
    )
