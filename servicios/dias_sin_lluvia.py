from datetime import date, timedelta

from sqlalchemy.orm import Session

from dominio.dias_sin_lluvia import dias_sin_lluvia
from infraestructura.repositorio import obtener_lluvias


def contar_dias_sin_lluvia(db: Session, hoy: date) -> dict:
    dias = dias_sin_lluvia(obtener_lluvias(db), hoy)
    if dias is None:
        return {"dias": None, "ultima_lluvia": None}
    return {"dias": dias, "ultima_lluvia": hoy - timedelta(days=dias)}
