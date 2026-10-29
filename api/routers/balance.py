from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencias import pronostico_actual
from dominio.prediccion import DatosPorDia
from infraestructura.database import get_db
from infraestructura.models import Bloque
from servicios.balance import calcular_balance
from servicios.prediccion import proyectar_balance

router = APIRouter()


@router.get("/balance")
def balance(db: Session = Depends(get_db)) -> dict[str, float]:
    bloques = db.query(Bloque).all()
    return {"balance_m³": calcular_balance(db, bloques)}


@router.get("/prediccion")
def prediccion(
    db: Session = Depends(get_db),
    pronostico: DatosPorDia = Depends(pronostico_actual),
) -> dict[str, DatosPorDia]:
    bloques = db.query(Bloque).all()
    return {"Balance proyectado": proyectar_balance(db, bloques, pronostico)}
