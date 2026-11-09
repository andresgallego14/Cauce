from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import config
from api.dependencias import pronostico_actual
from dominio.enums import Bocatoma
from dominio.prediccion import DatosPorDia
from infraestructura.database import get_db
from infraestructura.models import Bloque
from infraestructura.repositorio import obtener_reservorio
from servicios.balance import calcular_balance, fecha_ultimo_registro
from servicios.bombeo import calcular_plan_de_bombeo
from servicios.prediccion import proyectar_balance

router = APIRouter()


@router.get("/balance")
def balance(db: Session = Depends(get_db)) -> dict[str, Any]:
    bloques = db.query(Bloque).all()
    nivel = calcular_balance(db, bloques)
    capacidad = obtener_reservorio(db).capacidad_m3
    return {
        "balance_m³": nivel,
        "capacidad_m3": capacidad,
        "nivel_critico_m3": capacidad * config.PORCENTAJE_NIVEL_CRITICO,
        "datos_hasta": fecha_ultimo_registro(db),
    }


@router.get("/prediccion")
def prediccion(
    db: Session = Depends(get_db),
    pronostico: DatosPorDia = Depends(pronostico_actual),
) -> dict[str, Any]:
    bloques = db.query(Bloque).all()
    return {
        "Balance proyectado": proyectar_balance(db, bloques, pronostico),
        "datos_hasta": fecha_ultimo_registro(db),
    }


def horas_redondeadas(horas: dict[Bocatoma, float]) -> dict[str, float]:
    return {bocatoma.value: round(valor, 2) for bocatoma, valor in horas.items()}


@router.get("/bombeo")
def bombeo(
    db: Session = Depends(get_db),
    pronostico: DatosPorDia = Depends(pronostico_actual),
) -> dict[str, Any]:
    bloques = db.query(Bloque).all()
    plan = calcular_plan_de_bombeo(db, bloques, pronostico)
    return {
        "mantener": {
            "m3": round(plan.m3_para_mantener, 2),
            "horas": horas_redondeadas(plan.horas_para_mantener),
        },
        "llenar": {
            "m3": round(plan.m3_para_llenar, 2),
            "horas": horas_redondeadas(plan.horas_para_llenar),
        },
    }
