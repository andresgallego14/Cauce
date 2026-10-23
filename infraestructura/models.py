from infraestructura.database import Base 
from sqlalchemy import Column, Integer, String, Float, Date, Enum, ForeignKey
from dominio.enums import TipoMovimiento, Fuente, Bocatoma


def _valores(lista_cerrada):
    return [miembro.value for miembro in lista_cerrada]

class Bloque (Base):
    __tablename__="bloques"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    area_m2 = Column(Float, nullable=False)

class Reservorio(Base):
    __tablename__="reservorio"

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
    valor = Column (Float, nullable=False )
    bloques_id = Column(Integer, ForeignKey("bloques.id"))
    usuario = Column (String, nullable=False)
    notas = Column (String)
    