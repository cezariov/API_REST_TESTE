from fastapi import HTTPException, status


def unauthorized_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "message": "Invalid or missing authentication token.",
            "code": "UNAUTHORIZED",
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "message": "Admin access is required.",
            "code": "FORBIDDEN",
        },
    )
