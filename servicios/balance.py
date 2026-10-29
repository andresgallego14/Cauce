from sqlalchemy.orm import Session

import config
from dominio.balance import (
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


def calcular_balance(db: Session, bloques: list[Bloque]) -> float:
    if config.FECHA_INICIO_BALANCE is None or config.NIVEL_INICIAL_M3 is None:
        raise BalanceSinPuntoDeInicio(
            "Falta el punto de partida del balance: defina "
            "CAUCE_FECHA_INICIO_BALANCE y CAUCE_NIVEL_INICIAL_M3 "
            "en el archivo .env"
        )
    area_total_m2 = sum(bloque.area_m2 for bloque in bloques)
    movimientos = [
        (
            registro.fecha,
            movimiento_en_m3(registro.fuente, registro.valor, area_total_m2),
        )
        for registro in obtener_registros(db)
    ]
    reservorio = obtener_reservorio(db)
    return simular_balance(
        movimientos_desde(movimientos, config.FECHA_INICIO_BALANCE),
        reservorio.capacidad_m3,
        config.NIVEL_INICIAL_M3,
    )


def consumo_promedio_diario(db: Session) -> float:
    return promedio_diario_calendario(obtener_salidas(db))
