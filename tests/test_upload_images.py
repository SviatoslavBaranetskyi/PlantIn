from app.api.routes import images as images_route


class FakeEmbeddingService:
    def encode(self, image):
        return [1.0] + [0.0] * 511


class FakeVectorStore:
    upserted = []

    def __init__(self, client):
        self.client = client

    def upsert_embeddings(self, points):
        self.__class__.upserted.extend(points)


class FakeRequestRepository:
    created_request_id = None
    created_image_ids = None

    def create_request(self, image_ids, request_id=None):
        self.__class__.created_request_id = request_id
        self.__class__.created_image_ids = image_ids
        self.image_ids = image_ids
        return request_id


def test_upload_images_returns_request_id(client, png_image_bytes, monkeypatch):
    FakeVectorStore.upserted = []
    FakeRequestRepository.created_request_id = None
    FakeRequestRepository.created_image_ids = None
    monkeypatch.setattr(
        images_route,
        "get_embedding_service",
        lambda: FakeEmbeddingService(),
    )
    monkeypatch.setattr(images_route, "VectorStore", FakeVectorStore)
    monkeypatch.setattr(images_route, "RequestRepository", FakeRequestRepository)
    monkeypatch.setattr(images_route, "get_qdrant_client", lambda: object())

    response = client.post(
        "/images",
        files=[("files", ("plant.png", png_image_bytes, "image/png"))],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["uploaded"] == 1
    assert body["request_id"] == FakeRequestRepository.created_request_id
    assert len(FakeVectorStore.upserted) == 1
    assert len(FakeVectorStore.upserted[0]["vector"]) == 512
    assert FakeVectorStore.upserted[0]["payload"] == {
        "filename": "plant.png",
        "request_id": body["request_id"],
    }
    assert FakeRequestRepository.created_image_ids == [
        FakeVectorStore.upserted[0]["id"]
    ]


def test_upload_images_rejects_invalid_file(client):
    response = client.post(
        "/images",
        files=[("files", ("plant.txt", b"not an image", "text/plain"))],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image file"
