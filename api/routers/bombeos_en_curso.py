from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.esquemas import (
    BombeoEnCursoSalida,
    FinDeBombeoEntrada,
    InicioDeBombeoEntrada,
)
from infraestructura.database import get_db
from infraestructura.models import BombeoEnCurso
from servicios.registro_de_bombeo import (
    bombeos_en_curso,
    iniciar_bombeo,
    terminar_bombeo,
)

router = APIRouter()


@router.get("/bombeos-en-curso", response_model=list[BombeoEnCursoSalida])
def listar_bombeos_en_curso(db: Session = Depends(get_db)) -> list[BombeoEnCurso]:
    return bombeos_en_curso(db)


@router.post("/bombeo/inicio")
def crear_inicio_de_bombeo(
    datos: InicioDeBombeoEntrada, db: Session = Depends(get_db)
) -> dict[str, str]:
    iniciar_bombeo(db, datos.bocatoma, datos.inicio, datos.usuario, datetime.now())
    return {"mensaje": "Bombeo iniciado"}


@router.post("/bombeo/fin")
def crear_fin_de_bombeo(
    datos: FinDeBombeoEntrada, db: Session = Depends(get_db)
) -> dict[str, str | float]:
    m3 = terminar_bombeo(db, datos.bocatoma, datos.fin, datos.usuario, datetime.now())
    return {"mensaje": "Bombeo terminado", "m3": m3}
