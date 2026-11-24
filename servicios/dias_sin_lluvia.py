from datetime import date, timedelta

from sqlalchemy.orm import Session

from dominio.dias_sin_lluvia import dias_sin_lluvia
from infraestructura.repositorio import obtener_lluvias

CANTIDAD_DE_RECIENTES = 3


def contar_dias_sin_lluvia(db: Session, hoy: date) -> dict:
    lluvias = obtener_lluvias(db)
    recientes = [
        {"fecha": fecha, "mm": mm}
        for fecha, mm in sorted(lluvias, reverse=True)[:CANTIDAD_DE_RECIENTES]
    ]
    dias = dias_sin_lluvia(lluvias, hoy)
    if dias is None:
        return {
            "dias": None,
            "ultima_lluvia": None,
            "mm_ultima_lluvia": None,
            "recientes": recientes,
        }
    ultima_lluvia = hoy - timedelta(days=dias)
    mm_ultima_lluvia = max(mm for fecha, mm in lluvias if fecha == ultima_lluvia)
    return {
        "dias": dias,
        "ultima_lluvia": ultima_lluvia,
        "mm_ultima_lluvia": mm_ultima_lluvia,
        "recientes": recientes,
    }
