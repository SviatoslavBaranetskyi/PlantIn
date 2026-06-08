from app.core.config import settings
from app.services.vector_store import VectorStore, request_filter


class DuplicateDetector:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.threshold = settings.similarity_threshold

    def find_duplicates_for_request(self, request_id: str, image_ids: list[str]):
        request_points = self.vector_store.get_points(image_ids)
        request_id_set = set(image_ids)
        seen_pairs = set()
        duplicates = []
        filter_ = request_filter(request_id)

        for point in request_points:
            vector = point.vector
            if isinstance(vector, dict):
                vector = next(iter(vector.values()))

            results = self.vector_store.search_similar(
                vector=vector,
                limit=len(image_ids),
                score_threshold=self.threshold,
                query_filter=filter_,
            )

            for result in results:
                if result.id == point.id or result.id not in request_id_set:
                    continue

                pair = tuple(sorted((str(point.id), str(result.id))))
                if pair in seen_pairs:
                    continue

                seen_pairs.add(pair)
                duplicates.append(
                    {
                        "source_id": str(point.id),
                        "duplicate_id": str(result.id),
                        "score": result.score,
                        "source_filename": point.payload.get("filename"),
                        "duplicate_filename": result.payload.get("filename"),
                    }
                )

        return duplicates
