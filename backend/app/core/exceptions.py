from fastapi import Request
from fastapi.responses import JSONResponse

from app.utils.logger import get_logger

logger = get_logger("app.exceptions")


class DomainException(Exception):
    """
    Base exception for expected application/domain errors.

    These errors are safe to expose to API clients with their
    associated HTTP status code and problem details.
    """

    def __init__(
        self,
        detail: str,
        status_code: int = 400,
        type_uri: str = "about:blank",
    ):
        self.status_code = status_code
        self.detail = detail
        self.type_uri = type_uri

        super().__init__(detail)

class AuthError(DomainException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(detail=detail, status_code=401)

class ForbiddenError(DomainException):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail=detail, status_code=403)


async def domain_exception_handler(
    request: Request,
    exc: DomainException,
):
    """
    Convert a DomainException into a structured HTTP response.
    """

    logger.warning(
        "domain_exception",
        path=request.url.path,
        status_code=exc.status_code,
        detail=exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": exc.type_uri,
            "title": "Domain Error",
            "detail": exc.detail,
            "status": exc.status_code,
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Catch unexpected exceptions and return a safe generic response.

    The actual exception is logged server-side, while sensitive
    implementation details are not exposed to the client.
    """

    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
    )

    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "status": 500,
        },
    )