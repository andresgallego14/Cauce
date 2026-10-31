from dataclasses import dataclass
from datetime import date

HORAS_POR_DIA = 24


class LecturaIncongruente(Exception):
    """La lectura del medidor no puede ser real: se rechaza antes de guardarla."""


@dataclass(frozen=True)
class Lectura:
    fecha: date
    valor: float


def calcular_consumo(
    nueva: Lectura, anterior: Lectura | None, caudal_maximo_m3_h: float
) -> float:
    if anterior is None:
        return 0.0

    consumo = nueva.valor - anterior.valor
    if consumo < 0:
        raise LecturaIncongruente(
            f"La lectura {nueva.valor} es menor que la anterior "
            f"({anterior.valor} del {anterior.fecha:%d/%m/%Y}). "
            "Un medidor no retrocede: revisa el numero."
        )

    dias = max((nueva.fecha - anterior.fecha).days, 1)
    tope_m3 = caudal_maximo_m3_h * HORAS_POR_DIA * dias
    if consumo > tope_m3:
        raise LecturaIncongruente(
            f"El consumo de {consumo:.2f} m3 supera lo que este medidor puede "
            f"marcar en {dias} dia(s) ({tope_m3:.0f} m3). Revisa el numero."
        )

    return consumo
