from datetime import date, timedelta

from sqlalchemy.orm import Session

import config
from dominio.informe import resumir_por_dia
from infraestructura.models import Bloque
from servicios.balance import movimientos_del_balance


def armar_informe(
    db: Session, bloques: list[Bloque], dias: int | None, hoy: date
) -> dict:
    movimientos = movimientos_del_balance(db, bloques)
    desde = config.FECHA_INICIO_BALANCE
    if dias is not None:
        desde = max(desde, hoy - timedelta(days=dias - 1))
    return {
        "desde": desde,
        "hasta": hoy,
        "dias": resumir_por_dia(movimientos, desde, hoy),
    }
