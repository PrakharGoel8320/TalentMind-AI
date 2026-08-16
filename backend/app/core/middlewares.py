import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


logger = logging.getLogger("talentmind")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Adds a unique correlation/request ID to every request.

    The ID is taken from the incoming X-Correlation-ID header when
    available; otherwise a new UUID is generated.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID")

        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        request.state.correlation_id = correlation_id

        response = await call_next(request)

        response.headers["X-Correlation-ID"] = correlation_id

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs basic request/response information including method,
    path, status code, and request duration.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        try:
            response = await call_next(request)

            duration_ms = (time.perf_counter() - start_time) * 1000

            correlation_id = getattr(
                request.state,
                "correlation_id",
                "unknown",
            )

            logger.info(
                "%s %s -> %s (%.2f ms) [correlation_id=%s]",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                correlation_id,
            )

            return response

        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000

            correlation_id = getattr(
                request.state,
                "correlation_id",
                "unknown",
            )

            logger.exception(
                "%s %s -> ERROR (%.2f ms) [correlation_id=%s]",
                request.method,
                request.url.path,
                duration_ms,
                correlation_id,
            )

            raise