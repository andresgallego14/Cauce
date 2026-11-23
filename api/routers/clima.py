from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencias import pronostico_actual
from dominio.prediccion import DatosPorDia
from infraestructura.database import get_db
from servicios.prediccion import pronostico_con_lluvia_esperada

router = APIRouter()


@router.get("/pronostico")
def consultar_pronostico(
    pronostico: DatosPorDia = Depends(pronostico_actual),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return pronostico_con_lluvia_esperada(db, pronostico)
