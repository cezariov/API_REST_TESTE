from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate
from app.services import vehicle_service

router = APIRouter(prefix="/veiculos", tags=["veiculos"])


@router.get(
    "/relatorios/por-marca",
    status_code=status.HTTP_200_OK,
)
def count_vehicles_by_brand(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    return vehicle_service.count_active_by_brand(db)


@router.get("", response_model=list[VehicleResponse], status_code=status.HTTP_200_OK)
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


@router.get("/{vehicle_id}", response_model=VehicleResponse, status_code=status.HTTP_200_OK)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VehicleResponse:
    return vehicle_service.get_vehicle(db, vehicle_id)


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> VehicleResponse:
    return vehicle_service.create_vehicle(db, data)


@router.put("/{vehicle_id}", response_model=VehicleResponse, status_code=status.HTTP_200_OK)
def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> VehicleResponse:
    return vehicle_service.update_vehicle(db, vehicle_id, data)


@router.patch("/{vehicle_id}", response_model=VehicleResponse, status_code=status.HTTP_200_OK)
def patch_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> VehicleResponse:
    return vehicle_service.patch_vehicle(db, vehicle_id, data)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Response:
    vehicle_service.delete_vehicle(db, vehicle_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
