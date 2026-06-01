"""Application error types and the structured error contract.

Every error leaving the API uses the envelope ``{"error": {"code", "message"}}``.
Stack traces and upstream internals are never exposed to clients.
"""

from __future__ import annotations

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.models.common import ErrorBody, ErrorResponse

logger = structlog.get_logger(__name__)


class AppError(Exception):
    """Base application error mapped to a structured HTTP response."""

    code: str = "internal_error"
    message: str = "An unexpected error occurred."
    http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)


class BadRequestError(AppError):
    code = "bad_request"
    message = "The request was invalid."
    http_status = status.HTTP_400_BAD_REQUEST


class MissingClientIdError(BadRequestError):
    code = "missing_client_id"
    message = "A valid X-Client-Id header is required."


class CityNotFoundError(AppError):
    code = "city_not_found"
    message = "No matching city was found."
    http_status = status.HTTP_404_NOT_FOUND


class ResourceNotFoundError(AppError):
    code = "not_found"
    message = "The requested resource was not found."
    http_status = status.HTTP_404_NOT_FOUND


class UpstreamError(AppError):
    """Upstream returned an unexpected or error response (e.g. 5xx)."""

    code = "upstream_error"
    message = "The weather provider returned an error."
    http_status = status.HTTP_502_BAD_GATEWAY


class UpstreamUnavailableError(AppError):
    """Upstream is unreachable or its circuit breaker is open."""

    code = "upstream_unavailable"
    message = "The weather provider is currently unavailable."
    http_status = status.HTTP_503_SERVICE_UNAVAILABLE


def _envelope(code: str, message: str) -> dict[str, object]:
    return ErrorResponse(error=ErrorBody(code=code, message=message)).model_dump()


def register_exception_handlers(app: FastAPI) -> None:
    """Register handlers that render every error using the standard envelope."""

    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.http_status, content=_envelope(exc.code, exc.message))

    async def _handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_envelope("validation_error", "Request validation failed."),
        )

    async def _handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_exception", error=str(exc), exc_type=type(exc).__name__)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_envelope("internal_error", "An unexpected error occurred."),
        )

    app.add_exception_handler(AppError, _handle_app_error)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _handle_validation_error)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _handle_unexpected)
