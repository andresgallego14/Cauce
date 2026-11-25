from datetime import date

from sqlalchemy.orm import Session

from dominio.lluvia_del_mes import mes_anterior, resumir_lluvia_del_mes
from infraestructura.repositorio import obtener_lluvias


def comparar_lluvia_del_mes(db: Session, hoy: date) -> dict:
    lluvias = obtener_lluvias(db)
    anio_anterior, numero_mes_anterior = mes_anterior(hoy.year, hoy.month)
    return {
        "este_mes": resumir_lluvia_del_mes(lluvias, hoy.year, hoy.month),
        "mes_anterior": resumir_lluvia_del_mes(
            lluvias, anio_anterior, numero_mes_anterior
        ),
    }
