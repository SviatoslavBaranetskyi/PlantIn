from pydantic import BaseModel


class UploadImagesResponse(BaseModel):
    request_id: str
    uploaded: int


class DuplicateMatch(BaseModel):
    source_id: str
    duplicate_id: str
    score: float
    source_filename: str | None = None
    duplicate_filename: str | None = None


class DuplicatesResponse(BaseModel):
    request_id: str
    duplicates: list[DuplicateMatch]
    message: str
