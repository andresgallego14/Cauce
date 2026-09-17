from database import Base 
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import ForeignKey

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
    fecha = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    fuente = Column(String, nullable=False)
    bomba = Column(String, nullable=True)
    lectura_acumulada = Column(Float, nullable=True)
    valor = Column (Float, nullable=False )
    bloques_id = Column(Integer, ForeignKey("bloques.id"))
    usuario = Column (String, nullable=False)
    notas = Column (String)
    