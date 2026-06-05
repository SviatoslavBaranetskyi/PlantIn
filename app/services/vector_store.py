from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct


class VectorStore:
    def __init__(self, client: QdrantClient, collection_name: str = "images"):
        self.client = client
        self.collection_name = collection_name

        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=512,
                    distance=Distance.COSINE,
                ),
            )

    def upsert_embeddings(
        self,
        points: List[Dict[str, Any]],
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
        vector: List[float],
        limit: int = 5,
    ):
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
            with_payload=True,
        )