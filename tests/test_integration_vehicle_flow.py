from fastapi.testclient import TestClient

from app.models.user import User


def test_main_vehicle_flow(client: TestClient, admin_user: User) -> None:
    login_response = client.post(
        "/auth/login",
        json={
            "email": admin_user.email,
            "password": "admin123",
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]
    assert access_token

    headers = {"Authorization": f"Bearer {access_token}"}
    vehicle_payload = {
        "marca": "Toyota",
        "modelo": "Corolla",
        "ano": 2022,
        "cor": "Prata",
        "placa": "ABC1D23",
        "preco": 100000.0,
    }

    create_response = client.post(
        "/veiculos",
        json=vehicle_payload,
        headers=headers,
    )

    assert create_response.status_code == 201

    created_vehicle = create_response.json()
    vehicle_id = created_vehicle["id"]

    list_response = client.get("/veiculos", headers=headers)

    assert list_response.status_code == 200
    assert any(vehicle["id"] == vehicle_id for vehicle in list_response.json())

    filter_response = client.get(
        "/veiculos",
        params={
            "marca": "Toyota",
            "ano": 2022,
            "cor": "Prata",
        },
        headers=headers,
    )

    assert filter_response.status_code == 200

    filtered_vehicles = filter_response.json()
    assert len(filtered_vehicles) == 1
    assert filtered_vehicles[0]["id"] == vehicle_id
    assert filtered_vehicles[0]["placa"] == "ABC1D23"

    detail_response = client.get(f"/veiculos/{vehicle_id}", headers=headers)

    assert detail_response.status_code == 200

    vehicle_detail = detail_response.json()
    assert vehicle_detail["id"] == vehicle_id
    assert vehicle_detail["marca"] == vehicle_payload["marca"]
    assert vehicle_detail["modelo"] == vehicle_payload["modelo"]
    assert vehicle_detail["ano"] == vehicle_payload["ano"]
    assert vehicle_detail["cor"] == vehicle_payload["cor"]
    assert vehicle_detail["placa"] == vehicle_payload["placa"]
    assert vehicle_detail["preco"] == 20000.0
