import math
from dataclasses import dataclass

from dominio.bombeo import caudal_m3_h
from dominio.enums import Bocatoma

HORAS_DE_JORNADA = 9.0  # de 6:00 a 15:00
TOLERANCIA_M3 = 1e-9
SIN_SUMERGIBLE = (Bocatoma.BOCATOMA_1, Bocatoma.BOCATOMA_2)
TODAS_LAS_BOCATOMAS = (Bocatoma.BOCATOMA_1, Bocatoma.BOCATOMA_2, Bocatoma.SUMERGIBLE)


class PlanInvalido(Exception):
    pass


@dataclass(frozen=True)
class ResultadoDePlan:
    m3_por_bocatoma: dict[Bocatoma, float]
    m3_por_dia: float
    neto_por_dia: float
    dias_para_llenar: int | None


def validar_horas(horas: dict[Bocatoma, float]) -> None:
    for bocatoma, horas_al_dia in horas.items():
        if not 0 <= horas_al_dia <= HORAS_DE_JORNADA:
            raise PlanInvalido(
                f"{bocatoma.value}: las horas deben estar entre 0 y "
                f"{HORAS_DE_JORNADA:g} (jornada de 6:00 a 15:00)"
            )


def calcular_dias_para_llenar(m3_para_llenar: float, neto_por_dia: float) -> int | None:
    if m3_para_llenar <= 0:
        return 0
    if neto_por_dia <= 0:
        return None
    return math.ceil(round(m3_para_llenar / neto_por_dia, 6))


def evaluar_plan(
    horas: dict[Bocatoma, float], m3_para_llenar: float, m3_para_mantener: float
) -> ResultadoDePlan:
    validar_horas(horas)
    m3_por_bocatoma = {
        bocatoma: horas_al_dia * caudal_m3_h(bocatoma)
        for bocatoma, horas_al_dia in horas.items()
    }
    m3_por_dia = sum(m3_por_bocatoma.values())
    neto_por_dia = m3_por_dia - m3_para_mantener
    return ResultadoDePlan(
        m3_por_bocatoma=m3_por_bocatoma,
        m3_por_dia=m3_por_dia,
        neto_por_dia=neto_por_dia,
        dias_para_llenar=calcular_dias_para_llenar(m3_para_llenar, neto_por_dia),
    )


def redondear_al_minuto(horas: float) -> float:
    return math.ceil(round(horas * 60, 6)) / 60


def repartir_horas(
    m3_por_dia: float, bocatomas: tuple[Bocatoma, ...]
) -> dict[Bocatoma, float]:
    horas: dict[Bocatoma, float] = {}
    restante = m3_por_dia
    for bocatoma in bocatomas:
        if restante <= TOLERANCIA_M3:
            break
        horas_exactas = min(restante / caudal_m3_h(bocatoma), HORAS_DE_JORNADA)
        horas[bocatoma] = redondear_al_minuto(horas_exactas)
        restante -= horas_exactas * caudal_m3_h(bocatoma)
    if restante > TOLERANCIA_M3:
        maximo = m3_por_dia - restante
        mensaje = (
            f"Se necesitan {m3_por_dia:.1f} m³ al día y lo máximo es "
            f"{maximo:.1f} m³ con toda la jornada"
        )
        if Bocatoma.SUMERGIBLE not in bocatomas:
            mensaje += ": hace falta la Bocatoma Sumergible"
        raise PlanInvalido(mensaje)
    return horas