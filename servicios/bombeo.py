from sqlalchemy.orm import Session

import config
from dominio.bombeo import PlanDeBombeo, armar_plan
from dominio.prediccion import DatosPorDia, evaporacion_esperada_m3, lluvia_esperada_m3
from infraestructura.models import Bloque
from infraestructura.repositorio import obtener_reservorio
from servicios.balance import calcular_balance, consumo_promedio_diario


def aporte_neto_diario_m3(pronostico: DatosPorDia, area_total_m2: float) -> float:
    if not pronostico:
        return 0.0
    lluvias = lluvia_esperada_m3(pronostico, area_total_m2)
    evaporaciones = evaporacion_esperada_m3(
        pronostico, config.SUPERFICIE_RESERVORIO_M2, config.REDUCCION_POLISOMBRA
    )
    lluvia_total = sum(dia["lluvia_esperada_m3"] for dia in lluvias)
    evaporacion_total = sum(dia["evaporacion_m3"] for dia in evaporaciones)
    return (lluvia_total - evaporacion_total) / len(pronostico)


def calcular_plan_de_bombeo(
    db: Session, bloques: list[Bloque], pronostico: DatosPorDia
) -> PlanDeBombeo:
    area_total_m2 = sum(bloque.area_m2 for bloque in bloques)
    return armar_plan(
        nivel_actual_m3=calcular_balance(db, bloques),
        capacidad_m3=obtener_reservorio(db).capacidad_m3,
        consumo_diario_m3=consumo_promedio_diario(db),
        lluvia_diaria_m3=aporte_neto_diario_m3(pronostico, area_total_m2),
    )
