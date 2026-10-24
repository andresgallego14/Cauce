from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy.orm import Session
from infraestructura.database import get_db
from infraestructura.models import Bloque
from servicios.balance import calcular_balance
from typing import Optional
from pydantic import BaseModel, Field
from infraestructura.models import Registro
from infraestructura.clima import obtener_pronostico
from servicios.prediccion import proyectar_balance
from datetime import date
from dominio.enums import Fuente, Bocatoma

LARGO_MAX_USUARIO = 50
LARGO_MAX_NOTAS = 500
LARGO_MAX_NOMBRE_BLOQUE = 100

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje" : "Cauce API funcionando"}

@app.get("/balance")
def balance(db: Session = Depends(get_db)):
    bloques = db.query(Bloque).all()
    resultado = calcular_balance(db, bloques)
    return {"balance_m³": resultado}

@app.get("/bloques")
def listar_bloques(db: Session = Depends(get_db)):
    bloques = db.query(Bloque).all()
    resultado = []
    for bloque in bloques:
        resultado.append({"id": bloque.id, "nombre": bloque.nombre, "area_m2" : bloque.area_m2})
    return resultado

class RegistroEntrada (BaseModel):
    fecha : date
    fuente : Fuente
    valor : float = Field(ge=0)
    lectura_acumulada : Optional[float] = Field(default=None, ge=0)
    bocatoma : Optional[Bocatoma] = None
    usuario : str = Field(min_length=1, max_length=LARGO_MAX_USUARIO)
    notas : Optional[str] = Field(default=None, max_length=LARGO_MAX_NOTAS)

@app.post("/registro")
def crear_registro(datos: RegistroEntrada, db: Session = Depends(get_db)):
    nuevo_registro = Registro ( 
        fecha = datos.fecha, 
        tipo = datos.fuente.tipo,
        fuente = datos.fuente,
        valor = datos.valor,
        lectura_acumulada =  datos.lectura_acumulada,
        bocatoma = datos.bocatoma,
        usuario = datos.usuario, 
        notas = datos.notas
    )
    db.add(nuevo_registro)
    db.commit()
    return {"mensaje" : "Registro guardado"}

class BloqueEntrada (BaseModel):
    nombre : str = Field(min_length=1, max_length=LARGO_MAX_NOMBRE_BLOQUE)
    area_m2 : float = Field(gt=0)
    
@app.post("/bloques")
def crear_bloque(datos: BloqueEntrada, db: Session = Depends(get_db)):
    nuevo_bloque = Bloque(
        nombre = datos.nombre,
        area_m2 = datos.area_m2
    )
    db.add(nuevo_bloque)
    db.commit()
    return {"mensaje" : "Registro guardado"}

@app.get("/pronostico")
def pronostico():
    return obtener_pronostico()

@app.get("/prediccion")
def prediccion(db: Session = Depends(get_db)):
    bloques = db.query(Bloque).all()
    resultado = proyectar_balance(db, bloques, obtener_pronostico())
    return {"Balance proyectado" : resultado}