"""Health endpoint with per-dependency breakdown."""

from __future__ import annotations

from fastapi import APIRouter, Response, status

from app.dependencies import HealthServiceDep
from app.models.common import DependencyStatus, HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(service: HealthServiceDep, response: Response) -> HealthResponse:
    """Report overall and per-dependency health. 503 when a critical dep is down."""
    result = await service.check()
    if result.status is DependencyStatus.DOWN:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return result
