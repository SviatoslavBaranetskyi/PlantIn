import json
import uuid
from pathlib import Path


class RequestRepository:
    def __init__(self, path: str = "storage/requests.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self.path.write_text("{}")

    def create_request(
        self,
        image_ids: list[str],
        request_id: str | None = None,
    ) -> str:
        request_id = request_id or str(uuid.uuid4())

        data = self._read()
        data[request_id] = image_ids

        self._write(data)
        return request_id

    def get_images(self, request_id: str) -> list[str]:
        data = self._read()
        return data.get(request_id, [])

    def _read(self):
        return json.loads(self.path.read_text())

    def _write(self, data):
        self.path.write_text(json.dumps(data, indent=2))
