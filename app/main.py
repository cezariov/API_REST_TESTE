from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.api import auth_controller, vehicle_controller
from app.core.errors import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

app = FastAPI(
    title="Tinnova Veiculos API",
    description=(
        "API REST para gerenciamento de veiculos com autenticacao JWT, "
        "controle de perfis USER/ADMIN, soft delete, cache de cotacao do dolar "
        "e relatorios basicos."
    ),
    version="1.0.0",
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth_controller.router)
app.include_router(vehicle_controller.router)


@app.get(
    "/health",
    summary="Verificar saude da API",
    description="Retorna um status simples para confirmar que a aplicacao esta em execucao.",
    status_code=200,
)
def health_check() -> dict[str, str]:
    return {"status": "ok"}
