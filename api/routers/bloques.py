from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.esquemas import BloqueEntrada
from infraestructura.database import get_db
from infraestructura.models import Bloque

router = APIRouter()


@router.get("/bloques")
def listar_bloques(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    bloques = db.query(Bloque).all()
    return [
        {"id": bloque.id, "nombre": bloque.nombre, "area_m2": bloque.area_m2}
        for bloque in bloques
    ]


@router.post("/bloques")
def crear_bloque(datos: BloqueEntrada, db: Session = Depends(get_db)) -> dict[str, str]:
    db.add(Bloque(nombre=datos.nombre, area_m2=datos.area_m2))
    db.commit()
    return {"mensaje": "Registro guardado"}
