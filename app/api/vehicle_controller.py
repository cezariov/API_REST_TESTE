from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.error import ErrorResponse
from app.schemas.vehicle import (
    BrandReportResponse,
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
)
from app.services import vehicle_service

router = APIRouter(prefix="/veiculos", tags=["veiculos"])

ERROR_RESPONSES = {
    401: {"model": ErrorResponse, "description": "Token ausente ou inválido."},
    403: {"model": ErrorResponse, "description": "Permissão insuficiente."},
    404: {"model": ErrorResponse, "description": "Recurso não encontrado."},
    409: {"model": ErrorResponse, "description": "Conflito de dados."},
    422: {"model": ErrorResponse, "description": "Erro de validação."},
    500: {"model": ErrorResponse, "description": "Erro interno."},
}


@router.get(
    "/relatorios/por-marca",
    response_model=list[BrandReportResponse],
    status_code=status.HTTP_200_OK,
    summary="Relatório de veículos por marca",
    description="Retorna a quantidade de veículos ativos agrupados por marca.",
    responses={
        401: ERROR_RESPONSES[401],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    },
)
def count_vehicles_by_brand(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BrandReportResponse]:
    return vehicle_service.count_active_by_brand(db)


@router.get(
    "",
    response_model=list[VehicleResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar veículos",
    description=(
        "Lista veículos ativos com filtros opcionais por marca, ano, cor e faixa de preço. "
        "Disponível para usuários USER e ADMIN autenticados."
    ),
    responses={
        401: ERROR_RESPONSES[401],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    },
)
def list_vehicles(
    marca: str | None = None,
    ano: int | None = None,
    cor: str | None = None,
    minPreco: float | None = None,
    maxPreco: float | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[VehicleResponse]:
    filters = {
        "marca": marca,
        "ano": ano,
        "cor": cor,
        "minPreco": minPreco,
        "maxPreco": maxPreco,
    }

    return vehicle_service.list_vehicles(db, filters, skip, limit)


@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    status_code=status.HTTP_200_OK,
    summary="Detalhar veículo",
    description="Retorna os dados de um veículo ativo pelo ID.",
    responses={
        401: ERROR_RESPONSES[401],
        404: ERROR_RESPONSES[404],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    },
)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VehicleResponse:
    return vehicle_service.get_vehicle(db, vehicle_id)


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar veículo",
    description=(
        "Cria um veículo. O preço recebido deve estar em BRL e é convertido para USD "
        "antes de ser salvo. Requer perfil ADMIN."
    ),
    responses={
        201: {
            "description": "Veículo criado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "marca": "Toyota",
                        "modelo": "Corolla",
                        "ano": 2022,
                        "cor": "Prata",
                        "placa": "ABC1D23",
                        "preco": 20000.0,
                        "ativo": True,
                        "created_at": "2026-04-28T17:00:00",
                        "updated_at": "2026-04-28T17:00:00",
                    }
                }
            },
        },
        401: ERROR_RESPONSES[401],
        403: ERROR_RESPONSES[403],
        409: ERROR_RESPONSES[409],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    },
)
def create_vehicle(
    data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> VehicleResponse:
    return vehicle_service.create_vehicle(db, data)


@router.put(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar veículo completo",
    description="Atualiza todos os campos principais de um veículo ativo. Requer perfil ADMIN.",
    responses={
        401: ERROR_RESPONSES[401],
        403: ERROR_RESPONSES[403],
        404: ERROR_RESPONSES[404],
        409: ERROR_RESPONSES[409],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    },
)
def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> VehicleResponse:
    return vehicle_service.update_vehicle(db, vehicle_id, data)


@router.patch(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar veículo parcialmente",
    description="Atualiza parcialmente os campos enviados de um veículo ativo. Requer perfil ADMIN.",
    responses={
        401: ERROR_RESPONSES[401],
        403: ERROR_RESPONSES[403],
        404: ERROR_RESPONSES[404],
        409: ERROR_RESPONSES[409],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    },
)
def patch_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> VehicleResponse:
    return vehicle_service.patch_vehicle(db, vehicle_id, data)


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover veículo",
    description="Realiza soft delete do veículo, marcando-o como inativo. Requer perfil ADMIN.",
    responses={
        204: {"description": "Veículo removido com sucesso."},
        401: ERROR_RESPONSES[401],
        403: ERROR_RESPONSES[403],
        404: ERROR_RESPONSES[404],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    },
)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Response:
    vehicle_service.delete_vehicle(db, vehicle_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
