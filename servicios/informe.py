from datetime import date, timedelta

from sqlalchemy.orm import Session

import config
from dominio.informe import resumir_por_dia
from infraestructura.models import Bloque
from servicios.balance import movimientos_en_m3, revisar_punto_de_inicio


def armar_informe(
    db: Session, bloques: list[Bloque], dias: int | None, hoy: date
) -> dict:
    revisar_punto_de_inicio()
    desde = config.FECHA_INICIO_INFORME or config.FECHA_INICIO_BALANCE
    if dias is not None:
        desde = max(desde, hoy - timedelta(days=dias - 1))
    return {
        "desde": desde,
        "hasta": hoy,
        "dias": resumir_por_dia(movimientos_en_m3(db, bloques), desde, hoy),
    }
