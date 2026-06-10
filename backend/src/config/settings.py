import json
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "PayLink API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    HIDE_DOCS: bool = False

    # DATABASE CONFIG
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://payment:payment@localhost:5432/payment",
        description="Async SQLAlchemy DSN (asyncpg driver).",
    )

    # SECURITY
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 720  # 12 hours
    FERNET_KEY: str = "change-me-in-production"

    # CORS CONFIG — accepts a JSON array OR a comma-separated string via CORS_ORIGINS.
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:4173"

    @property
    def cors_origins_list(self) -> list[str]:
        raw = self.CORS_ORIGINS.strip()
        if not raw:
            return []
        if raw.startswith("["):
            try:
                return [str(o) for o in json.loads(raw)]
            except json.JSONDecodeError:
                pass
        return [o.strip() for o in raw.split(",") if o.strip()]

    # KKIAPAY CONFIG
    KKIAPAY_API_URL: str = "https://api.kkiapay.me"
    KKIAPAY_SANDBOX_API_URL: str = "https://api-sandbox.kkiapay.me"

    # SEED CONFIG (bootstrap admin + demo entity)
    SEED_ADMIN_EMAIL: str = "change-me-in-production"
    SEED_ADMIN_PASSWORD: str = "change-me-in-production"
    SEED_ENTITY_SLUG: str = "change-me-in-production"
    SEED_ENTITY_NAME: str = "change-me-in-production"
    SEED_KKIAPAY_PUBLIC_KEY: str = "your-sandbox-public-key"
    SEED_KKIAPAY_PRIVATE_KEY: str = "your-sandbox-private-key"
    SEED_KKIAPAY_SECRET: str = "your-sandbox-secret"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
