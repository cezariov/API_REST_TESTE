import pytest
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException

from app.services import vehicle_service


def _vehicle_data(
    placa: str,
    marca: str = "Toyota",
    modelo: str = "Corolla",
    ano: int = 2022,
    cor: str = "Prata",
    preco: float = 100000.0,
) -> dict:
    return {
        "marca": marca,
        "modelo": modelo,
        "ano": ano,
        "cor": cor,
        "placa": placa,
        "preco": preco,
    }


def test_create_vehicle_success(db_session: Session) -> None:
    vehicle = vehicle_service.create_vehicle(
        db_session,
        _vehicle_data(placa="ABC1D23"),
    )

    assert vehicle.id is not None
    assert vehicle.ativo is True
    assert vehicle.marca == "Toyota"
    assert vehicle.modelo == "Corolla"
    assert vehicle.ano == 2022
    assert vehicle.cor == "Prata"
    assert vehicle.placa == "ABC1D23"
    assert vehicle.preco == 20000.0


def test_create_vehicle_duplicate_plate(db_session: Session) -> None:
    vehicle_service.create_vehicle(db_session, _vehicle_data(placa="ABC1D23"))

    with pytest.raises(HTTPException) as exc_info:
        vehicle_service.create_vehicle(db_session, _vehicle_data(placa="ABC1D23"))

    assert exc_info.value.status_code == 409


def test_list_vehicles_with_combined_filters(db_session: Session) -> None:
    expected_vehicle = vehicle_service.create_vehicle(
        db_session,
        _vehicle_data(
            placa="ABC1D23",
            marca="Toyota",
            modelo="Corolla",
            ano=2022,
            cor="Prata",
        ),
    )
    vehicle_service.create_vehicle(
        db_session,
        _vehicle_data(
            placa="DEF4G56",
            marca="Toyota",
            modelo="Hilux",
            ano=2023,
            cor="Prata",
        ),
    )
    vehicle_service.create_vehicle(
        db_session,
        _vehicle_data(
            placa="HIJ7K89",
            marca="Honda",
            modelo="Civic",
            ano=2022,
            cor="Preto",
        ),
    )

    vehicles = vehicle_service.list_vehicles(
        db_session,
        filters={"marca": "Toyota", "ano": 2022, "cor": "Prata"},
        skip=0,
        limit=10,
    )

    assert len(vehicles) == 1
    assert vehicles[0].id == expected_vehicle.id
    assert vehicles[0].placa == "ABC1D23"


def test_update_vehicle_not_found(db_session: Session) -> None:
    with pytest.raises(HTTPException) as exc_info:
        vehicle_service.update_vehicle(
            db_session,
            vehicle_id=999,
            data=_vehicle_data(placa="ABC1D23"),
        )

    assert exc_info.value.status_code == 404


def test_patch_vehicle_not_found(db_session: Session) -> None:
    with pytest.raises(HTTPException) as exc_info:
        vehicle_service.patch_vehicle(
            db_session,
            vehicle_id=999,
            data={"cor": "Azul"},
        )

    assert exc_info.value.status_code == 404


def test_soft_delete_vehicle(db_session: Session) -> None:
    vehicle = vehicle_service.create_vehicle(
        db_session,
        _vehicle_data(placa="ABC1D23"),
    )

    deleted_vehicle = vehicle_service.delete_vehicle(db_session, vehicle.id)

    assert deleted_vehicle.ativo is False

    with pytest.raises(HTTPException) as exc_info:
        vehicle_service.get_vehicle(db_session, vehicle.id)

    assert exc_info.value.status_code == 404
