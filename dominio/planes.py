import math
from dataclasses import dataclass

from dominio.bombeo import caudal_m3_h
from dominio.enums import Bocatoma

HORAS_DE_JORNADA = 9.0  # de 6:00 a 15:00
TOLERANCIA_M3 = 1e-9
SIN_SUMERGIBLE = (Bocatoma.BOCATOMA_1, Bocatoma.BOCATOMA_2)
TODAS_LAS_BOCATOMAS = (Bocatoma.BOCATOMA_1, Bocatoma.BOCATOMA_2, Bocatoma.SUMERGIBLE)
PORCENTAJE_PARA_MANTENER = 0.85
DIAS_DE_UNA_SEMANA = 7


class PlanInvalido(Exception):
    pass


@dataclass(frozen=True)
class ResultadoDePlan:
    m3_por_bocatoma: dict[Bocatoma, float]
    m3_por_dia: float
    neto_por_dia: float
    dias_para_llenar: int | None


@dataclass(frozen=True)
class PlanSugerido:
    nombre: str
    meta: str
    horas: dict[Bocatoma, float]


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


def maximo_por_dia(bocatomas: tuple[Bocatoma, ...]) -> float:
    return sum(HORAS_DE_JORNADA * caudal_m3_h(bocatoma) for bocatoma in bocatomas)


def dias_minimos_para_llenar(
    m3_para_llenar: float, m3_para_mantener: float, bocatomas: tuple[Bocatoma, ...]
) -> int | None:
    neto_maximo = maximo_por_dia(bocatomas) - m3_para_mantener
    return calcular_dias_para_llenar(m3_para_llenar, neto_maximo)


def horas_para_llenar_en(
    dias: int,
    m3_para_llenar: float,
    m3_para_mantener: float,
    bocatomas: tuple[Bocatoma, ...],
) -> dict[Bocatoma, float]:
    return repartir_horas(m3_para_mantener + m3_para_llenar / dias, bocatomas)


def hasta_donde_alcance(
    m3_por_dia: float, bocatomas: tuple[Bocatoma, ...]
) -> dict[Bocatoma, float]:
    try:
        return repartir_horas(m3_por_dia, bocatomas)
    except PlanInvalido:
        return {bocatoma: HORAS_DE_JORNADA for bocatoma in bocatomas}


def llenar_lo_antes_posible(
    m3_objetivo: float, m3_para_mantener: float, bocatomas: tuple[Bocatoma, ...]
) -> dict[Bocatoma, float]:
    dias = dias_minimos_para_llenar(m3_objetivo, m3_para_mantener, bocatomas)
    if dias is None:
        return {bocatoma: HORAS_DE_JORNADA for bocatoma in bocatomas}
    m3_extra = m3_objetivo / dias if dias > 0 else 0.0
    return hasta_donde_alcance(m3_para_mantener + m3_extra, bocatomas)


def nivel_critico_m3(capacidad_m3: float, porcentaje_critico: float) -> float:
    return capacidad_m3 * porcentaje_critico


def planes_del_sistema(
    nivel_m3: float,
    capacidad_m3: float,
    m3_para_mantener: float,
    porcentaje_critico: float,
) -> list[PlanSugerido]:
    m3_para_llenar = max(capacidad_m3 - nivel_m3, 0.0)
    planes = [
        PlanSugerido(
            nombre="Mantener",
            meta="Reponer solo lo que se gasta en el día.",
            horas=hasta_donde_alcance(m3_para_mantener, SIN_SUMERGIBLE),
        ),
        PlanSugerido(
            nombre="Llenar lo antes posible",
            meta="Llegar al 100% en el menor número de días, sin la Sumergible.",
            horas=llenar_lo_antes_posible(
                m3_para_llenar, m3_para_mantener, SIN_SUMERGIBLE
            ),
        ),
        PlanSugerido(
            nombre="Llenar en una semana",
            meta="Llegar al 100% en 7 días, con menos horas cada día.",
            horas=hasta_donde_alcance(
                m3_para_mantener + m3_para_llenar / DIAS_DE_UNA_SEMANA,
                SIN_SUMERGIBLE,
            ),
        ),
    ]
    critico = nivel_critico_m3(capacidad_m3, porcentaje_critico)
    if nivel_m3 < critico:
        planes.insert(
            0,
            PlanSugerido(
                nombre="Salir de crítico",
                meta="Pasar del nivel crítico cuanto antes; se permite la Sumergible.",
                horas=llenar_lo_antes_posible(
                    critico - nivel_m3, m3_para_mantener, TODAS_LAS_BOCATOMAS
                ),
            ),
        )
    return planes


def recomendar_plan(
    nivel_m3: float, capacidad_m3: float, porcentaje_critico: float
) -> str:
    if nivel_m3 < nivel_critico_m3(capacidad_m3, porcentaje_critico):
        return "Salir de crítico"
    if nivel_m3 < capacidad_m3 * PORCENTAJE_PARA_MANTENER:
        return "Llenar lo antes posible"
    return "Mantener"
