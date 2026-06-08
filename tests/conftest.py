from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def png_image_bytes():
    buffer = BytesIO()
    Image.new("RGB", (32, 32), color="green").save(buffer, format="PNG")
    return buffer.getvalue()
