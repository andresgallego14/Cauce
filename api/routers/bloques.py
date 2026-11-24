from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.acceso import verificar_clave_admin
from api.esquemas import BloqueEntrada, ClaveEntrada, EdicionDeBloqueEntrada
from infraestructura.database import get_db
from infraestructura.models import Bloque
from servicios.bloques import editar_bloque, eliminar_bloque

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


@router.post("/bloques/{id_bloque}/editar")
def editar_un_bloque(
    id_bloque: int, datos: EdicionDeBloqueEntrada, db: Session = Depends(get_db)
) -> dict[str, str]:
    verificar_clave_admin(datos.clave)
    editar_bloque(db, id_bloque, datos.nombre, datos.area_m2)
    return {"mensaje": "Bloque actualizado"}


@router.post("/bloques/{id_bloque}/eliminar")
def eliminar_un_bloque(
    id_bloque: int, datos: ClaveEntrada, db: Session = Depends(get_db)
) -> dict[str, str]:
    verificar_clave_admin(datos.clave)
    eliminar_bloque(db, id_bloque)
    return {"mensaje": "Bloque eliminado"}
