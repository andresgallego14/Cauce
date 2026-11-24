import enum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)

from dominio.enums import Bocatoma, Fuente, TipoMovimiento
from infraestructura.database import Base


def _valores(lista_cerrada: type[enum.Enum]) -> list[str]:
    return [miembro.value for miembro in lista_cerrada]


class Bloque(Base):
    __tablename__ = "bloques"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    area_m2 = Column(Float, nullable=False)


class Reservorio(Base):
    __tablename__ = "reservorio"

    id = Column(Integer, primary_key=True)
    capacidad_m3 = Column(Float, nullable=False)


class Registro(Base):
    __tablename__ = "registros"

    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    tipo = Column(Enum(TipoMovimiento, values_callable=_valores), nullable=False)
    fuente = Column(Enum(Fuente, values_callable=_valores), nullable=False)
    bocatoma = Column(Enum(Bocatoma, values_callable=_valores), nullable=True)
    lectura_acumulada = Column(Float, nullable=True)
    valor = Column(Float, nullable=False)
    bloques_id = Column(Integer, ForeignKey("bloques.id"))
    usuario = Column(String, nullable=False)
    notas = Column(String)


class BombeoEnCurso(Base):
    __tablename__ = "bombeos_en_curso"

    id = Column(Integer, primary_key=True)
    bocatoma = Column(
        Enum(Bocatoma, values_callable=_valores), nullable=False, unique=True
    )
    inicio = Column(DateTime, nullable=False)
    usuario = Column(String, nullable=False)


class Anulacion(Base):
    __tablename__ = "anulaciones"

    id = Column(Integer, primary_key=True)
    registro_id = Column(
        Integer, ForeignKey("registros.id"), nullable=False, unique=True
    )
    motivo = Column(String, nullable=False)
    usuario = Column(String, nullable=False)
    momento = Column(DateTime, nullable=False)


class PlanGuardado(Base):
    __tablename__ = "planes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False, unique=True)
    meta = Column(String, nullable=False)
    modo = Column(String, nullable=False)
    horas_pequena = Column(Float, nullable=True)
    horas_grande = Column(Float, nullable=True)
    horas_sumergible = Column(Float, nullable=True)
    dias = Column(Integer, nullable=True)
    permite_sumergible = Column(Boolean, nullable=False, default=False)
    usuario = Column(String, nullable=False)
    creado = Column(DateTime, nullable=False)
