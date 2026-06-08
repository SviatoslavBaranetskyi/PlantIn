from fastapi import APIRouter, HTTPException

from app.db.qdrant import get_qdrant_client
from app.models.responses import DuplicatesResponse
from app.repositories.request_repository import RequestRepository
from app.services.duplicate_detector import DuplicateDetector
from app.services.vector_store import VectorStore

router = APIRouter()


@router.get("/duplicates/{request_id}", response_model=DuplicatesResponse)
async def get_duplicates(request_id: str):
    repo = RequestRepository()
    image_ids = repo.get_images(request_id)

    if not image_ids:
        raise HTTPException(status_code=404, detail="Request not found")

    vector_store = VectorStore(get_qdrant_client())
    detector = DuplicateDetector(vector_store)
    duplicates = detector.find_duplicates_for_request(request_id, image_ids)

    message = "Duplicates found" if duplicates else "No duplicates found"
    return DuplicatesResponse(
        request_id=request_id,
        duplicates=duplicates,
        message=message,
    )
