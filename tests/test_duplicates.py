from types import SimpleNamespace

from app.api.routes import duplicates as duplicates_route


class FakeRequestRepository:
    def get_images(self, request_id):
        if request_id == "request-1":
            return ["image-1", "image-2"]
        return []


class FakeVectorStore:
    def __init__(self, client):
        self.client = client

    def get_points(self, ids):
        return [
            SimpleNamespace(
                id="image-1",
                vector=[1.0] + [0.0] * 511,
                payload={"filename": "first.png", "request_id": "request-1"},
            ),
            SimpleNamespace(
                id="image-2",
                vector=[1.0] + [0.0] * 511,
                payload={"filename": "second.png", "request_id": "request-1"},
            ),
        ]

    def search_similar(
        self,
        vector,
        limit=5,
        score_threshold=None,
        query_filter=None,
    ):
        self.query_filter = query_filter
        return [
            SimpleNamespace(
                id="image-1",
                score=1.0,
                payload={"filename": "first.png", "request_id": "request-1"},
            ),
            SimpleNamespace(
                id="image-2",
                score=0.99,
                payload={"filename": "second.png", "request_id": "request-1"},
            ),
        ]


def test_get_duplicates_returns_matches(client, monkeypatch):
    monkeypatch.setattr(duplicates_route, "RequestRepository", FakeRequestRepository)
    monkeypatch.setattr(duplicates_route, "VectorStore", FakeVectorStore)
    monkeypatch.setattr(duplicates_route, "get_qdrant_client", lambda: object())

    response = client.get("/duplicates/request-1")

    assert response.status_code == 200
    body = response.json()
    assert body["request_id"] == "request-1"
    assert body["message"] == "Duplicates found"
    assert body["duplicates"] == [
        {
            "source_id": "image-1",
            "duplicate_id": "image-2",
            "score": 0.99,
            "source_filename": "first.png",
            "duplicate_filename": "second.png",
        }
    ]


def test_get_duplicates_returns_404_for_unknown_request(client, monkeypatch):
    monkeypatch.setattr(duplicates_route, "RequestRepository", FakeRequestRepository)

    response = client.get("/duplicates/missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "Request not found"
