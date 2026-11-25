from datetime import date

from sqlalchemy.orm import Session

import config
from dominio.balance import (
    PERDIDA_INICIAL_LLUVIA_MM,
    lluvia_en_m3,
    lluvia_util_mm,
    movimiento_en_m3,
    movimientos_desde,
    promedio_diario_calendario,
    simular_balance,
)
from infraestructura.models import Bloque
from infraestructura.repositorio import (
    obtener_registros,
    obtener_reservorio,
    obtener_salidas,
)


class BalanceSinPuntoDeInicio(Exception):
    pass


def revisar_punto_de_inicio() -> None:
    if config.FECHA_INICIO_BALANCE is None or config.NIVEL_INICIAL_M3 is None:
        raise BalanceSinPuntoDeInicio(
            "Falta el punto de partida del balance: defina "
            "CAUCE_FECHA_INICIO_BALANCE y CAUCE_NIVEL_INICIAL_M3 "
            "en el archivo .env"
        )


def movimientos_del_balance(
    db: Session, bloques: list[Bloque]
) -> list[tuple[date, float]]:
    revisar_punto_de_inicio()
    area_total_m2 = sum(bloque.area_m2 for bloque in bloques)
    movimientos = [
        (
            registro.fecha,
            movimiento_en_m3(registro.fuente, registro.valor, area_total_m2),
        )
        for registro in obtener_registros(db)
    ]
    return movimientos_desde(movimientos, config.FECHA_INICIO_BALANCE)


def calcular_balance(db: Session, bloques: list[Bloque]) -> float:
    movimientos = movimientos_del_balance(db, bloques)
    reservorio = obtener_reservorio(db)
    return simular_balance(
        movimientos, reservorio.capacidad_m3, config.NIVEL_INICIAL_M3
    )


def consumo_promedio_diario(db: Session) -> float:
    return promedio_diario_calendario(obtener_salidas(db))


def fecha_ultimo_registro(db: Session) -> date | None:
    return max((registro.fecha for registro in obtener_registros(db)), default=None)


def convertir_lluvia(db: Session, mm: float) -> dict[str, float]:
    area_total_m2 = sum(bloque.area_m2 for bloque in db.query(Bloque).all())
    return {
        "mm_medidos": mm,
        "perdida_mm": PERDIDA_INICIAL_LLUVIA_MM,
        "mm_utiles": lluvia_util_mm(mm),
        "m3": round(lluvia_en_m3(mm, area_total_m2), 2),
    }
