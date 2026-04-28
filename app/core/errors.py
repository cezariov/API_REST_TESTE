from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.schemas.error import ErrorResponse

ERROR_CODES = {
    status.HTTP_400_BAD_REQUEST: "bad_request",
    status.HTTP_401_UNAUTHORIZED: "unauthorized",
    status.HTTP_403_FORBIDDEN: "forbidden",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_409_CONFLICT: "conflict",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "validation_error",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "internal_error",
    status.HTTP_503_SERVICE_UNAVAILABLE: "service_unavailable",
}

DEFAULT_MESSAGES = {
    status.HTTP_400_BAD_REQUEST: "Bad request.",
    status.HTTP_401_UNAUTHORIZED: "Unauthorized.",
    status.HTTP_403_FORBIDDEN: "Forbidden.",
    status.HTTP_404_NOT_FOUND: "Resource not found.",
    status.HTTP_409_CONFLICT: "Conflict.",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "Validation error.",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal server error.",
    status.HTTP_503_SERVICE_UNAVAILABLE: "Service unavailable.",
}


def unauthorized_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access is required.",
    )


def bad_request_error(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def not_found_error(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


def conflict_error(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def service_unavailable_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=message,
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    message, details = _extract_error_detail(exc.detail, exc.status_code)
    code = ERROR_CODES.get(exc.status_code, _status_to_code(exc.status_code))

    return JSONResponse(
        status_code=exc.status_code,
        content=_error_content(message=message, code=code, details=details),
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_content(
            message="Validation error.",
            code=ERROR_CODES[status.HTTP_422_UNPROCESSABLE_ENTITY],
            details=jsonable_encoder(exc.errors()),
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_content(
            message=DEFAULT_MESSAGES[status.HTTP_500_INTERNAL_SERVER_ERROR],
            code=ERROR_CODES[status.HTTP_500_INTERNAL_SERVER_ERROR],
        ),
    )


def _extract_error_detail(detail: object, status_code: int) -> tuple[str, object | None]:
    if isinstance(detail, dict):
        message = str(detail.get("message") or DEFAULT_MESSAGES.get(status_code, "Error."))
        details = detail.get("details")
        return message, details

    if isinstance(detail, str):
        return detail, None

    return DEFAULT_MESSAGES.get(status_code, "Error."), detail


def _error_content(
    message: str,
    code: str,
    details: object | None = None,
) -> dict[str, object]:
    response = ErrorResponse(message=message, code=code, details=details)
    return response.model_dump(exclude_none=True)


def _status_to_code(status_code: int) -> str:
    if status_code >= 500:
        return "internal_error"

    return "error"
