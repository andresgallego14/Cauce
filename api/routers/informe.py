from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from infraestructura.database import get_db
from infraestructura.models import Bloque
from servicios.informe import armar_informe

router = APIRouter()


@router.get("/informe")
def informe(
    dias: int | None = Query(None, ge=1, le=366),
    db: Session = Depends(get_db),
) -> dict:
    bloques = db.query(Bloque).all()
    return armar_informe(db, bloques, dias, date.today())
