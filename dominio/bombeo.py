from dataclasses import dataclass

from dominio.enums import Bocatoma

MINUTOS_POR_HORA = 60
LITROS_POR_M3 = 1000


def caudal_m3_h(bocatoma: Bocatoma) -> float:
    return bocatoma.caudal_l_min * MINUTOS_POR_HORA / LITROS_POR_M3


def horas_de_bombeo(m3_faltantes: float, bocatoma: Bocatoma) -> float:
    if m3_faltantes <= 0:
        return 0.0
    return m3_faltantes / caudal_m3_h(bocatoma)


@dataclass(frozen=True)
class PlanDeBombeo:
    m3_para_mantener: float
    m3_para_llenar: float
    horas_para_mantener: dict[Bocatoma, float]
    horas_para_llenar: dict[Bocatoma, float]


def horas_por_bocatoma(m3: float) -> dict[Bocatoma, float]:
    return {bocatoma: horas_de_bombeo(m3, bocatoma) for bocatoma in Bocatoma}


def armar_plan(
    nivel_actual_m3: float,
    capacidad_m3: float,
    consumo_diario_m3: float,
    lluvia_diaria_m3: float,
) -> PlanDeBombeo:
    m3_para_mantener = max(consumo_diario_m3 - lluvia_diaria_m3, 0.0)
    m3_para_llenar = max(capacidad_m3 - nivel_actual_m3, 0.0)
    return PlanDeBombeo(
        m3_para_mantener=m3_para_mantener,
        m3_para_llenar=m3_para_llenar,
        horas_para_mantener=horas_por_bocatoma(m3_para_mantener),
        horas_para_llenar=horas_por_bocatoma(m3_para_llenar),
    )
