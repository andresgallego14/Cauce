from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import config
from api.dependencias import pronostico_actual
from api.esquemas import PlanEntrada
from dominio.prediccion import DatosPorDia
from infraestructura.database import get_db
from infraestructura.models import Bloque, PlanGuardado
from infraestructura.repositorio import obtener_reservorio
from servicios.balance import calcular_balance
from servicios.bombeo import calcular_plan_de_bombeo
from servicios.planes import crear_plan, evaluar_planes

router = APIRouter()


@router.get("/planes")
def listar_planes(
    db: Session = Depends(get_db),
    pronostico: DatosPorDia = Depends(pronostico_actual),
) -> dict:
    bloques = db.query(Bloque).all()
    plan_de_hoy = calcular_plan_de_bombeo(db, bloques, pronostico)
    guardados = db.query(PlanGuardado).order_by(PlanGuardado.id).all()
    return evaluar_planes(
        guardados,
        nivel_m3=calcular_balance(db, bloques),
        capacidad_m3=obtener_reservorio(db).capacidad_m3,
        m3_para_mantener=plan_de_hoy.m3_para_mantener,
        porcentaje_critico=config.PORCENTAJE_NIVEL_CRITICO,
    )


@router.post("/planes")
def crear_un_plan(datos: PlanEntrada, db: Session = Depends(get_db)) -> dict:
    plan = crear_plan(db, **datos.model_dump(), ahora=datetime.now())
    return {"id": plan.id, "nombre": plan.nombre}
