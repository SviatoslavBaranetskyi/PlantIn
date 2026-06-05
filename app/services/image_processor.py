from io import BytesIO

from PIL import Image


class ImageProcessor:
    ALLOWED_FORMATS = {"JPEG", "PNG"}

    def __init__(self, max_size_mb: int = 10):
        self.max_size_mb = max_size_mb

    def validate_image(self, file_bytes: bytes) -> None:
        if len(file_bytes) > self.max_size_mb * 1024 * 1024:
            raise ValueError("Image exceeds max size limit (10MB)")

        try:
            image = Image.open(BytesIO(file_bytes))
            image.verify()
        except Exception:
            raise ValueError("Invalid image file")

        if image.format not in self.ALLOWED_FORMATS:
            raise ValueError(f"Unsupported format: {image.format}")

    def load_image(self, file_bytes: bytes) -> Image.Image:
        return Image.open(BytesIO(file_bytes)).convert("RGB")

    def preprocess(self, image: Image.Image, size: int = 224) -> Image.Image:
        return image.resize((size, size))