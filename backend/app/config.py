"""Application configuration sourced from environment variables.

All tunable values (hosts, TTLs, timeouts, thresholds) live here and are
populated from the environment via pydantic-settings. Nothing is hardcoded at
the call sites so the same image runs in dev, CI, and production unchanged.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Runtime
    app_env: Literal["dev", "prod"] = "dev"
    log_level: str = "INFO"

    # CORS: comma-separated list of allowed frontend origins.
    cors_origins: str = "http://localhost:3000"

    # Redis cache
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 600
    cache_coord_precision: int = 2

    # MongoDB persistence
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db_name: str = "weather"

    # History
    history_max_items: int = 20

    # Open-Meteo upstream base URLs (keyless, CC BY 4.0).
    geocoding_base_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    forecast_base_url: str = "https://api.open-meteo.com/v1/forecast"
    air_quality_base_url: str = "https://air-quality-api.open-meteo.com/v1/air-quality"

    # httpx timeouts (seconds)
    http_connect_timeout: float = 3.0
    http_read_timeout: float = 8.0

    # tenacity retry
    retry_max_attempts: int = 3
    retry_initial_backoff: float = 0.2
    retry_max_backoff: float = 2.0

    # pybreaker circuit breaker (per upstream)
    breaker_fail_max: int = 5
    breaker_reset_timeout: int = 30

    # health check upstream probe timeout (seconds)
    health_upstream_timeout: float = 2.0

    @property
    def allowed_origins(self) -> list[str]:
        """Parse the comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "prod"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
