from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and `.env`."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CareCloud Voice Patient Registration"
    environment: str = "development"
    log_level: str = "INFO"
    allowed_origins: str = Field(default="http://localhost:3000,http://localhost:8000")

    database_url: str | None = None
    vapi_api_key: str | None = None
    vapi_webhook_secret: str | None = None

    @field_validator("database_url")
    @classmethod
    def use_psycopg_driver(cls, value: str | None) -> str | None:
        """Accept Neon's default URL while consistently using the installed psycopg v3 driver."""
        if value is None:
            return None
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
