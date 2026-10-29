from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from dominio.enums import Bocatoma, Fuente, TipoMovimiento

LARGO_MAX_USUARIO = 50
LARGO_MAX_NOTAS = 500
LARGO_MAX_NOMBRE_BLOQUE = 100


class RegistroEntrada(BaseModel):
    fecha: date
    fuente: Fuente
    valor: float = Field(ge=0)
    lectura_acumulada: Optional[float] = Field(default=None, ge=0)
    bocatoma: Optional[Bocatoma] = None
    usuario: str = Field(min_length=1, max_length=LARGO_MAX_USUARIO)
    notas: Optional[str] = Field(default=None, max_length=LARGO_MAX_NOTAS)


class RegistroSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fecha: date
    fuente: Fuente
    tipo: TipoMovimiento
    valor: float
    usuario: str
    notas: Optional[str] = None


class BloqueEntrada(BaseModel):
    nombre: str = Field(min_length=1, max_length=LARGO_MAX_NOMBRE_BLOQUE)
    area_m2: float = Field(gt=0)
