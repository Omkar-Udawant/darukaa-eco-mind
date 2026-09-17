"""Central configuration. All env-driven, safe defaults for local demo."""
from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Darukaa.Earth Environmental Intelligence"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "sqlite:///./darukaa.db"
    REDIS_URL: str = ""  # empty => in-memory memory manager
    QDRANT_URL: str = ""  # empty => local vector store
    QDRANT_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    EMBEDDING_PROVIDER: str = "hash"  # hash | openai
    VECTOR_BACKEND: str = "local"  # local | chroma | qdrant
    CHROMA_DIR: str = "./chroma_db"

    CORS_ORIGINS: str = "http://localhost:3000"

    # Reasoning thresholds
    MIN_DIMENSIONS_FOR_RECOMMENDATION: int = 3
    LOW_SOC_THRESHOLD: float = 1.0  # % organic carbon
    LOW_RAINFALL_THRESHOLD_MM: float = 600.0
    HIGH_TEMP_THRESHOLD_C: float = 32.0


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
