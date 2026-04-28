from fastapi.testclient import TestClient


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _vehicle_payload(
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


def test_list_vehicles_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/veiculos")

    assert response.status_code == 401


def test_create_vehicle_with_user_token_returns_403(
    client: TestClient,
    user_token: str,
) -> None:
    response = client.post(
        "/veiculos",
        json=_vehicle_payload(placa="ABC1D23"),
        headers=_auth_header(user_token),
    )

    assert response.status_code == 403


def test_create_vehicle_with_admin_returns_201(
    client: TestClient,
    admin_token: str,
) -> None:
    response = client.post(
        "/veiculos",
        json=_vehicle_payload(placa="ABC1D23"),
        headers=_auth_header(admin_token),
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["ativo"] is True
    assert data["marca"] == "Toyota"
    assert data["modelo"] == "Corolla"
    assert data["ano"] == 2022
    assert data["cor"] == "Prata"
    assert data["placa"] == "ABC1D23"
    assert data["preco"] == 20000.0


def test_create_vehicle_duplicate_plate_returns_409(
    client: TestClient,
    admin_token: str,
) -> None:
    headers = _auth_header(admin_token)
    payload = _vehicle_payload(placa="ABC1D23")

    client.post("/veiculos", json=payload, headers=headers)
    response = client.post("/veiculos", json=payload, headers=headers)

    assert response.status_code == 409


def test_list_vehicles_with_filters(
    client: TestClient,
    admin_token: str,
    user_token: str,
) -> None:
    admin_headers = _auth_header(admin_token)

    expected_response = client.post(
        "/veiculos",
        json=_vehicle_payload(
            placa="ABC1D23",
            marca="Toyota",
            modelo="Corolla",
            ano=2022,
            cor="Prata",
        ),
        headers=admin_headers,
    )
    client.post(
        "/veiculos",
        json=_vehicle_payload(
            placa="DEF4G56",
            marca="Toyota",
            modelo="Hilux",
            ano=2023,
            cor="Prata",
        ),
        headers=admin_headers,
    )
    client.post(
        "/veiculos",
        json=_vehicle_payload(
            placa="HIJ7K89",
            marca="Honda",
            modelo="Civic",
            ano=2022,
            cor="Preto",
        ),
        headers=admin_headers,
    )

    response = client.get(
        "/veiculos",
        params={"marca": "Toyota", "ano": 2022, "cor": "Prata"},
        headers=_auth_header(user_token),
    )

    assert response.status_code == 200

    vehicles = response.json()
    assert len(vehicles) == 1
    assert vehicles[0]["id"] == expected_response.json()["id"]
    assert vehicles[0]["placa"] == "ABC1D23"


def test_get_vehicle_detail(
    client: TestClient,
    admin_token: str,
    user_token: str,
) -> None:
    create_response = client.post(
        "/veiculos",
        json=_vehicle_payload(placa="ABC1D23"),
        headers=_auth_header(admin_token),
    )
    vehicle_id = create_response.json()["id"]

    response = client.get(
        f"/veiculos/{vehicle_id}",
        headers=_auth_header(user_token),
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == vehicle_id
    assert data["placa"] == "ABC1D23"
    assert data["marca"] == "Toyota"


def test_delete_vehicle_soft_delete(
    client: TestClient,
    admin_token: str,
    user_token: str,
) -> None:
    create_response = client.post(
        "/veiculos",
        json=_vehicle_payload(placa="ABC1D23"),
        headers=_auth_header(admin_token),
    )
    vehicle_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/veiculos/{vehicle_id}",
        headers=_auth_header(admin_token),
    )

    assert delete_response.status_code == 204

    detail_response = client.get(
        f"/veiculos/{vehicle_id}",
        headers=_auth_header(user_token),
    )

    assert detail_response.status_code == 404


def test_count_vehicles_by_brand_report(
    client: TestClient,
    admin_token: str,
    user_token: str,
) -> None:
    admin_headers = _auth_header(admin_token)

    client.post(
        "/veiculos",
        json=_vehicle_payload(placa="ABC1D23", marca="Toyota"),
        headers=admin_headers,
    )
    client.post(
        "/veiculos",
        json=_vehicle_payload(placa="DEF4G56", marca="Toyota"),
        headers=admin_headers,
    )
    client.post(
        "/veiculos",
        json=_vehicle_payload(placa="HIJ7K89", marca="Honda"),
        headers=admin_headers,
    )

    response = client.get(
        "/veiculos/relatorios/por-marca",
        headers=_auth_header(user_token),
    )

    assert response.status_code == 200

    report = {item["marca"]: item["quantidade"] for item in response.json()}
    assert report == {"Honda": 1, "Toyota": 2}
