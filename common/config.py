"""Base configuration with Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List, Optional


class ServiceSettings(BaseSettings):
    """Base settings that all microservices inherit."""
    APP_NAME: str = "ReceiptBuddy"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://receiptbuddy:receiptbuddy123@localhost:5432/receiptbuddy"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT (shared secret across services)
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Service URLs (for inter-service communication)
    AUTH_SERVICE_URL: str = "http://auth:8001"
    FINANCE_SERVICE_URL: str = "http://finance:8002"
    HR_SERVICE_URL: str = "http://hr:8003"
    INTELLIGENCE_SERVICE_URL: str = "http://intelligence:8004"

    # External services
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "receiptbuddy"
    MINIO_SECRET_KEY: str = "receiptbuddy123"
    MINIO_BUCKET: str = "receipts"

    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_URL: str = "http://localhost:6333"

    OLLAMA_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "gemma4:e4b"
    EMBEDDING_MODEL: str = "nomic-embed-text-v1.5"

    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow service-specific settings
