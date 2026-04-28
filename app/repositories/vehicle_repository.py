from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle


def create_vehicle(db: Session, vehicle_data: Any) -> Vehicle:
    data = _to_dict(vehicle_data)
    vehicle = Vehicle(**data)

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle


def get_by_id(db: Session, vehicle_id: int) -> Vehicle | None:
    return db.get(Vehicle, vehicle_id)


def get_by_plate(db: Session, placa: str) -> Vehicle | None:
    statement = select(Vehicle).where(
        Vehicle.placa == placa,
        Vehicle.ativo.is_(True),
    )
    return db.scalar(statement)


def list_vehicles(
    db: Session,
    filters: dict[str, Any] | None,
    skip: int,
    limit: int,
) -> list[Vehicle]:
    filters = filters or {}
    statement = select(Vehicle).where(Vehicle.ativo.is_(True))

    if marca := filters.get("marca"):
        statement = statement.where(Vehicle.marca == marca)

    ano = filters.get("ano")
    if ano is not None:
        statement = statement.where(Vehicle.ano == ano)

    if cor := filters.get("cor"):
        statement = statement.where(Vehicle.cor == cor)

    min_preco = filters.get("minPreco")
    if min_preco is not None:
        statement = statement.where(Vehicle.preco >= min_preco)

    max_preco = filters.get("maxPreco")
    if max_preco is not None:
        statement = statement.where(Vehicle.preco <= max_preco)

    statement = statement.offset(skip).limit(limit)

    return list(db.scalars(statement).all())


def count_active_by_brand(db: Session) -> list[dict[str, Any]]:
    statement = (
        select(Vehicle.marca, func.count(Vehicle.id))
        .where(Vehicle.ativo.is_(True))
        .group_by(Vehicle.marca)
        .order_by(Vehicle.marca)
    )

    return [
        {"marca": marca, "quantidade": quantidade}
        for marca, quantidade in db.execute(statement).all()
    ]


def update_vehicle(db: Session, vehicle: Vehicle, data: Any) -> Vehicle:
    update_data = _to_dict(data, exclude_unset=True)

    for field, value in update_data.items():
        setattr(vehicle, field, value)

    vehicle.updated_at = datetime.utcnow()

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle


def soft_delete_vehicle(db: Session, vehicle: Vehicle) -> Vehicle:
    vehicle.ativo = False
    vehicle.updated_at = datetime.utcnow()

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle


def _to_dict(data: Any, exclude_unset: bool = False) -> dict[str, Any]:
    if hasattr(data, "model_dump"):
        return data.model_dump(exclude_unset=exclude_unset)

    if isinstance(data, dict):
        return data

    return dict(data)
