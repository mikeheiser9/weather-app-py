"""Shared models and enums: units, error contract, and health responses."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Units(StrEnum):
    """Unit system requested by the client."""

    METRIC = "metric"
    IMPERIAL = "imperial"


class ErrorBody(BaseModel):
    """Inner body of the standard error envelope."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error envelope returned for every error: {"error": {...}}."""

    error: ErrorBody


class DependencyStatus(StrEnum):
    """Status of a single health dependency."""

    OK = "ok"
    DEGRADED = "degraded"
    DOWN = "down"


class BreakerState(StrEnum):
    """Circuit breaker state as reported by /health."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class DependencyHealth(BaseModel):
    """Health of a single dependency."""

    status: DependencyStatus
    detail: str | None = None


class HealthResponse(BaseModel):
    """Aggregate health payload with per-dependency breakdown."""

    status: DependencyStatus
    redis: DependencyHealth
    mongo: DependencyHealth
    upstream: DependencyHealth
    breakers: dict[str, BreakerState] = Field(default_factory=dict)
