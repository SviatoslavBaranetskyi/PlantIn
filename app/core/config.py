from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Duplicate Image Detection Service"
    project_version: str = "1.0.0"

    api_prefix: str = "/api/v1"

    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)

    max_image_size_mb: int = 10

    similarity_threshold: float = 0.98

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()