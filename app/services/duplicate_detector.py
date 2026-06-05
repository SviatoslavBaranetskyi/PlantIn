from app.core.config import settings
from app.services.vector_store import VectorStore


class DuplicateDetector:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.threshold = settings.similarity_threshold

    def find_duplicates(self, vector: list[float]):
        results = self.vector_store.search_similar(
            vector=vector,
            limit=10,
        )

        duplicates = []

        for r in results:
            if r.score >= self.threshold:
                duplicates.append(
                    {
                        "id": r.id,
                        "score": r.score,
                        "payload": r.payload,
                    }
                )

        return duplicates