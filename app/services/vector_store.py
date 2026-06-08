from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings


class VectorStore:
    def __init__(
        self,
        client: QdrantClient,
        collection_name: str = settings.qdrant_collection,
        vector_size: int = settings.embedding_size,
    ):
        self.client = client
        self.collection_name = collection_name
        self.vector_size = vector_size

        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def upsert_embeddings(
        self,
        points: list[dict[str, Any]],
    ) -> None:
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=p["id"],
                    vector=p["vector"],
                    payload=p.get("payload", {}),
                )
                for p in points
            ],
        )

    def search_similar(
        self,
        vector: list[float],
        limit: int = 5,
        score_threshold: float | None = None,
        query_filter: Filter | None = None,
    ):
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
            with_payload=True,
        )

    def get_points(self, ids: list[str]):
        return self.client.retrieve(
            collection_name=self.collection_name,
            ids=ids,
            with_vectors=True,
            with_payload=True,
        )


def request_filter(request_id: str) -> Filter:
    return Filter(
        must=[
            FieldCondition(
                key="request_id",
                match=MatchValue(value=request_id),
            )
        ]
    )
