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
    pass


class VehicleUpdate(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano: Optional[int] = None
    cor: Optional[str] = None
    placa: Optional[str] = None
    preco: Optional[float] = None


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

    model_config = ConfigDict(from_attributes=True)
