import os
from functools import lru_cache
from pydantic import BaseModel, Field, ValidationError


class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    DB_PATH: str = Field(..., description="Filesystem path to the SQLite database file")
    JWT_SECRET: str = Field(..., description="Secret key used to sign JWTs")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24, description="Access token expiry in minutes")
    CORS_ALLOW_ORIGINS: list[str] = Field(default_factory=lambda: ["*"], description="Allowed CORS origins")


# PUBLIC_INTERFACE
@lru_cache
def get_settings() -> Settings:
    """Return application settings read from environment, cached for runtime."""
    try:
        # Note: Env variables must be set in .env by orchestrator.
        settings = Settings(
            DB_PATH=os.getenv("DB_PATH", "").strip(),
            JWT_SECRET=os.getenv("JWT_SECRET", "").strip(),
            JWT_ALGORITHM=os.getenv("JWT_ALGORITHM", "HS256").strip(),
            ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")),
            CORS_ALLOW_ORIGINS=[o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")],
        )
    except ValidationError as e:
        raise RuntimeError(f"Invalid settings: {e}") from e

    if not settings.DB_PATH:
        raise RuntimeError("DB_PATH environment variable is required but not set.")
    if not settings.JWT_SECRET:
        raise RuntimeError("JWT_SECRET environment variable is required but not set.")
    return settings
