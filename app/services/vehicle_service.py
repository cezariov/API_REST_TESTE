from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.repositories import vehicle_repository
from app.services.exchange_service import get_usd_to_brl

REQUIRED_VEHICLE_FIELDS = {"marca", "modelo", "ano", "cor", "placa", "preco"}


def create_vehicle(db: Session, data: Any) -> Vehicle:
    vehicle_data = _to_dict(data)

    existing_vehicle = vehicle_repository.get_by_plate(db, vehicle_data["placa"])
    if existing_vehicle:
        raise _conflict_error("A vehicle with this plate already exists.")

    vehicle_data["preco"] = _convert_brl_to_usd(vehicle_data["preco"])

    return vehicle_repository.create_vehicle(db, vehicle_data)


def update_vehicle(db: Session, vehicle_id: int, data: Any) -> Vehicle:
    vehicle = get_vehicle(db, vehicle_id)
    update_data = _to_dict(data, exclude_unset=True)

    missing_fields = REQUIRED_VEHICLE_FIELDS - update_data.keys()
    if missing_fields:
        raise _bad_request_error("PUT requires all vehicle fields.")

    empty_fields = [field for field in REQUIRED_VEHICLE_FIELDS if update_data[field] is None]
    if empty_fields:
        raise _bad_request_error("PUT fields cannot be null.")

    _ensure_unique_plate(db, update_data["placa"], vehicle.id)

    return vehicle_repository.update_vehicle(db, vehicle, update_data)


def patch_vehicle(db: Session, vehicle_id: int, data: Any) -> Vehicle:
    vehicle = get_vehicle(db, vehicle_id)
    update_data = _to_dict(data, exclude_unset=True)

    if "placa" in update_data:
        _ensure_unique_plate(db, update_data["placa"], vehicle.id)

    return vehicle_repository.update_vehicle(db, vehicle, update_data)


def delete_vehicle(db: Session, vehicle_id: int) -> Vehicle:
    vehicle = get_vehicle(db, vehicle_id)
    return vehicle_repository.soft_delete_vehicle(db, vehicle)


def get_vehicle(db: Session, vehicle_id: int) -> Vehicle:
    vehicle = vehicle_repository.get_by_id(db, vehicle_id)

    if vehicle is None or not vehicle.ativo:
        raise _not_found_error("Vehicle not found.")

    return vehicle


def list_vehicles(
    db: Session,
    filters: dict[str, Any] | None,
    skip: int,
    limit: int,
) -> list[Vehicle]:
    return vehicle_repository.list_vehicles(db, filters, skip, limit)


def count_active_by_brand(db: Session) -> list[dict[str, Any]]:
    return vehicle_repository.count_active_by_brand(db)


def _ensure_unique_plate(db: Session, placa: str, current_vehicle_id: int) -> None:
    existing_vehicle = vehicle_repository.get_by_plate(db, placa)

    if existing_vehicle and existing_vehicle.id != current_vehicle_id:
        raise _conflict_error("A vehicle with this plate already exists.")


def _convert_brl_to_usd(price_brl: float) -> float:
    usd_to_brl = get_usd_to_brl()
    return round(float(price_brl) / usd_to_brl, 2)


def _to_dict(data: Any, exclude_unset: bool = False) -> dict[str, Any]:
    if hasattr(data, "model_dump"):
        return data.model_dump(exclude_unset=exclude_unset)

    if isinstance(data, dict):
        return data.copy()

    return dict(data)


def _bad_request_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"message": message, "code": "BAD_REQUEST"},
    )


def _not_found_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"message": message, "code": "VEHICLE_NOT_FOUND"},
    )


def _conflict_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"message": message, "code": "VEHICLE_PLATE_CONFLICT"},
    )
