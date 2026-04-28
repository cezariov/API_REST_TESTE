from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class VehicleBase(BaseModel):
    marca: str
    modelo: str
    ano: int
    cor: str
    placa: str
    preco: float


class VehicleCreate(VehicleBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2022,
                "cor": "Prata",
                "placa": "ABC1D23",
                "preco": 100000.0,
            }
        }
    )


class VehicleUpdate(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano: Optional[int] = None
    cor: Optional[str] = None
    placa: Optional[str] = None
    preco: Optional[float] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2023,
                "cor": "Preto",
                "placa": "ABC1D23",
                "preco": 120000.0,
            }
        }
    )


class VehicleResponse(BaseModel):
    id: int
    marca: str
    modelo: str
    ano: int
    cor: str
    placa: str
    preco: float
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
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
        },
    )


class BrandReportResponse(BaseModel):
    marca: str
    quantidade: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "marca": "Toyota",
                "quantidade": 2,
            }
        }
    )
