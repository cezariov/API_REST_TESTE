from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.api import auth_controller, vehicle_controller
from app.core.config import settings
from app.core.errors import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

app = FastAPI(title=settings.project_name)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth_controller.router)
app.include_router(vehicle_controller.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
